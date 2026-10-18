import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

from .analysis import analyze
from .errors import CLIConfigError, StreamStatsError
from .models import Event
from .parsers import parse_csv, parse_jsonl
from .report import make_report


def all_events(
    files: list[str],
    file_format: str,
    skip_invalid: bool,
    skipped: dict[str, int],
) -> Iterator[Event]:  # делаем функцию
    for file in files:  # проходимся по одному файлу
        if file_format == "csv":
            events = parse_csv(file, skip_invalid, skipped)
        else:
            events = parse_jsonl(file, skip_invalid, skipped)
        yield from events  # выдаем последовательно каждый файл


def main() -> int:
    parser = argparse.ArgumentParser()  # подключили парсер
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,  # обязательно должен быть написан анализ
    )  # сохрани подкоманды в то что напишут
    analyze_parser = subparsers.add_parser("analyze")  # добавили сабпарсер анализа
    analyze_parser.add_argument(
        "file", nargs="+"
    )  # сказали что все файлы нужно сохранять в file и их может быть >=1
    analyze_parser.add_argument(
        "--format", choices=["csv", "jsonl"], required=True
    )  # после слова --формат обязаны идти одно из двух значений
    analyze_parser.add_argument("--output")
    analyze_parser.add_argument(
        "--skip-invalid",  # добавили скип с булевым флагом
        action="store_true",  # если встретится-тру
    )
    args = parser.parse_args()
    skipped = {"count": 0}


    try:
        if args.output:  # проверка на одинаковый входной\выходной файл
            output_path = Path(args.output).resolve()

            for input_file in args.file:
                if Path(input_file).resolve() == output_path:
                    raise CLIConfigError("Входной и выходной файлы не должны совпадать")
        events = all_events(args.file, args.format, args.skip_invalid, skipped)
        stat = analyze(events)
        report = make_report(stat)

        report["skipped"] = skipped["count"]

        if args.output:
            with open(args.output, "w", encoding="utf-8") as file:
                json.dump(report, file, indent=4, ensure_ascii=False)
        else:
            print(json.dumps(report, indent=4, ensure_ascii=False))

    except StreamStatsError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Ошибка при работе с файлом: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":  # это как бы защита от импортированных файлов
    sys.exit(main())  # если бы просто импортировали, то код бы не запустился
