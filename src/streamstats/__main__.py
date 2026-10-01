import argparse


def main():
    parser = argparse.ArgumentParser()  # подключили парсер
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,     #обязательно должен быть написан анализ
        )  # сохрани подкоманды в то что напишут
    analyze_parser = subparsers.add_parser("analyze")  # добавили сабпарсер анализа
    analyze_parser.add_argument(
        "file", nargs="+"
    )  # сказали что все файлы нужно сохранять в files и их может быть >=1
    analyze_parser.add_argument(
        "--format", choices=["csv", "jsonl"], required=True
    )  # после слова --формат обязаны идти одно из двух значений
    analyze_parser.add_argument(
        "--output", required=True
    )
    analyze_parser.add_argument(
        "--skip-invalid",         #добавили скип с булевым флагом
        action="store_true",    #если встретится-тру
    )
    args = parser.parse_args()

    print(args)


if __name__ == "__main__":  # это как бы защита от импортированных файлов
    main()  # если бы просто импортировали, то код бы не запустился
