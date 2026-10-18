from collections.abc import Iterable
from datetime import datetime

from .models import Event

AnalysisResult = tuple[  # для аннотации вывода
    int,
    dict[str, int],
    dict[str, int],
    dict[str, int],
    datetime | None,
    datetime | None,
    list[tuple[str, int]],
]


def analyze(events: Iterable[Event]) -> AnalysisResult:
    total = 0

    levels = {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }

    sources = {}  # создали пустой словарь для новых значений

    error_sources = {}  # создали словарь только для ошибок

    first_time = None
    last_time = None

    for event in events:  # идем по одному событию за раз
        total += 1
        levels[event.level] += 1
        sources[event.source] = sources.get(event.source, 0) + 1

        if event.level in ("ERROR", "CRITICAL"):
            error_sources[event.source] = error_sources.get(event.source, 0) + 1

        if first_time is None or event.timestamp < first_time:
            first_time = event.timestamp

        if last_time is None or event.timestamp > last_time:
            last_time = event.timestamp

    top5_errors = sorted(error_sources.items(), key=lambda item: (-item[1], item[0]))[
        :5
    ]  # сортируем ошибки сначала по значениям, потом в алфовитном порядке

    return total, levels, sources, error_sources, first_time, last_time, top5_errors
