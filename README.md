# StreamStats — анализатор потоковых событий

## Описание проекта

StreamStats — консольное приложение на Python для потокового анализа событий из файлов CSV и JSONL.

Программа обрабатывает записи, проверяет корректность данных, собирает статистику и формирует отчёт в формате JSON.

## Возможности

- Чтение файлов CSV и JSONL.
- Обработка нескольких файлов за один запуск.
- Потоковая обработка событий с помощью генераторов.
- Проверка полей `timestamp`, `level`, `source`, `message`.
- Подсчёт общего количества событий.
- Подсчёт событий по уровням и источникам.
- Подсчёт ошибок уровней `ERROR` и `CRITICAL` по источникам.
- Поиск первого и последнего события по времени.
- Определение пяти источников с наибольшим количеством ошибок.
- Пропуск некорректных записей с помощью `--skip-invalid`.
- Сохранение отчёта в JSON-файл.

## Требования

- Python 3.11 или новее.
- pip.

## Формат входных данных

Каждое событие содержит четыре поля:

| Поле | Описание |
|---|---|
| `timestamp` | Дата и время в формате ISO 8601 |
| `level` | Уровень события |
| `source` | Источник события |
| `message` | Текст сообщения |

Допустимые уровни событий: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

Пример CSV:

```csv
timestamp,level,source,message
2026-10-18T10:00:00,INFO,api,Started
2026-10-18T10:05:00,ERROR,db,Connection failed
```

Пример JSONL:

```jsonl
{"timestamp":"2026-10-18T10:00:00","level":"INFO","source":"api","message":"Started"}
{"timestamp":"2026-10-18T10:05:00","level":"ERROR","source":"db","message":"Connection failed"}
```

## Запуск программы

Анализ JSONL:

```bash
python -m streamstats analyze events.jsonl --format jsonl
```

Анализ CSV:

```bash
python -m streamstats analyze events.csv --format csv
```

Анализ нескольких файлов:

```bash
python -m streamstats analyze first.jsonl second.jsonl --format jsonl
```

Сохранение отчёта:

```bash
python -m streamstats analyze events.jsonl --format jsonl --output result.json
```

Пропуск некорректных записей:

```bash
python -m streamstats analyze events.jsonl --format jsonl --skip-invalid
```

При использовании `--skip-invalid` некорректные записи пропускаются, предупреждения выводятся в stderr, а количество пропущенных записей сохраняется в поле `skipped`.

Без этого флага некорректная запись приводит к ошибке.

## Пример результата

```json
{
    "total": 2,
    "levels": {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 0,
        "ERROR": 1,
        "CRITICAL": 0
    },
    "sources": {
        "api": 1,
        "db": 1
    },
    "error_sources": {
        "db": 1
    },
    "first_time": "2026-10-18T10:00:00",
    "last_time": "2026-10-18T10:05:00",
    "top5_errors": [
        ["db", 1]
    ],
    "skipped": 0
}
```

Источники в `top5_errors` сортируются по убыванию количества ошибок, а при равенстве — по алфавиту.

## Тестирование

Запуск всех тестов:

```bash
python -m pytest -v
```

Проверка стиля:

```bash
python -m ruff check .
```

Проверка форматирования:

```bash
python -m black --check .
```

Проект содержит 30 автоматических тестов для анализатора, парсеров и интерфейса командной строки.

## Структура проекта

Основные файлы:

```text
python-lab-2/
├── src/
│   └── streamstats/
│       ├── __init__.py
│       ├── __main__.py
│       ├── analysis.py
│       ├── errors.py
│       ├── models.py
│       ├── parsers.py
│       └── report.py
├── tests/
│   ├── test_analysis.py
│   ├── test_parsers.py
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

Основная логика разделена на несколько модулей:

- `models.py` — модель события.
- `parsers.py` — чтение и проверка данных.
- `analysis.py` — подсчёт статистики.
- `report.py` — формирование отчёта.
- `errors.py` — пользовательские исключения.
- `__main__.py` — обработка аргументов командной строки.

## Коды завершения

- `0` — программа успешно завершилась.
- `2` — ошибка входных данных, файла или аргументов командной строки.