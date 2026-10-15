import argparse
from .parsers import parse_csv, parse_jsonl
from .analysis import analyze



def all_events(files, format, skip_invalid): #делаем функцию
    for file in files: #проходимся по одному файлу
        if format == 'csv':
            events = parse_csv(file, skip_invalid)
        else:
            events = parse_jsonl(file, skip_invalid)
    yield from events #выдаем последовательно каждый файл




def main():
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


    events = all_events(args.file, args.format, args.skip_invalid)
    stat = analyze(events)
    print(stat)
    return args


if __name__ == "__main__":  # это как бы защита от импортированных файлов
    main()  # если бы просто импортировали, то код бы не запустился
