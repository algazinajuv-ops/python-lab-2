from datetime import datetime

from streamstats.analysis import analyze
from streamstats.models import Event


def test_empty_events():  # Пустой список событий
    result = analyze([])

    assert result[0] == 0
    assert result[1] == {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }
    assert result[2] == {}
    assert result[3] == {}
    assert result[4] is None
    assert result[5] is None
    assert result[6] == []


def test_two_events():  # Два события разных уровней
    events = [
        Event(datetime(2026, 10, 16, 10, 0), "INFO", "api", "Started"),
        Event(datetime(2026, 10, 16, 10, 5), "ERROR", "db", "Failed"),
    ]

    result = analyze(events)

    assert result[0] == 2
    assert result[1] == {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 0,
        "ERROR": 1,
        "CRITICAL": 0,
    }
    assert result[2] == {"api": 1, "db": 1}
    assert result[3] == {"db": 1}
    assert result[4] == datetime(2026, 10, 16, 10, 0)
    assert result[5] == datetime(2026, 10, 16, 10, 5)
    assert result[6] == [("db", 1)]


def test_unsorted_events():  # События расположены не по времени
    events = [
        Event(datetime(2026, 10, 16, 15, 0), "INFO", "api", "A"),
        Event(datetime(2026, 10, 16, 9, 0), "ERROR", "db", "B"),
        Event(datetime(2026, 10, 16, 12, 0), "WARNING", "worker", "C"),
    ]

    result = analyze(events)

    assert result[0] == 3
    assert result[1] == {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 1,
        "ERROR": 1,
        "CRITICAL": 0,
    }
    assert result[2] == {"api": 1, "db": 1, "worker": 1}
    assert result[3] == {"db": 1}
    assert result[4] == datetime(2026, 10, 16, 9, 0)
    assert result[5] == datetime(2026, 10, 16, 15, 0)
    assert result[6] == [("db", 1)]


def test_top5_errors():  # Топ-5 источников ошибок
    counts = {
        "api": 3,
        "db": 5,
        "cache": 3,
        "worker": 2,
        "auth": 1,
        "network": 4,
    }

    events = []

    for source, count in counts.items():
        for _ in range(count):
            events.append(
                Event(
                    datetime(2026, 10, 16, 10, 0),
                    "ERROR",
                    source,
                    "Test error",
                )
            )

    result = analyze(events)

    assert result[0] == 18
    assert result[1]["ERROR"] == 18
    assert result[2] == counts
    assert result[3] == counts
    assert result[4] == datetime(2026, 10, 16, 10, 0)
    assert result[5] == datetime(2026, 10, 16, 10, 0)

    assert result[6] == [
        ("db", 5),
        ("network", 4),
        ("api", 3),
        ("cache", 3),
        ("worker", 2),
    ]


def test_single_event():  # Одно событие
    event = Event(
        datetime(2026, 10, 18, 12, 30),
        "INFO",
        "server",
        "Started",
    )

    result = analyze([event])

    assert result[0] == 1
    assert result[1]["INFO"] == 1
    assert result[2] == {"server": 1}
    assert result[3] == {}
    assert result[4] == datetime(2026, 10, 18, 12, 30)
    assert result[5] == datetime(2026, 10, 18, 12, 30)
    assert result[6] == []


def test_critical_error():  # CRITICAL тоже считается ошибкой
    events = [
        Event(datetime(2026, 10, 18, 10, 0), "ERROR", "db", "Error"),
        Event(datetime(2026, 10, 18, 10, 1), "CRITICAL", "db", "Crash"),
        Event(datetime(2026, 10, 18, 10, 2), "CRITICAL", "api", "Down"),
    ]

    result = analyze(events)

    assert result[0] == 3
    assert result[1]["ERROR"] == 1
    assert result[1]["CRITICAL"] == 2
    assert result[3] == {"db": 2, "api": 1}
    assert result[6] == [("db", 2), ("api", 1)]


def test_non_error_levels():  # INFO, WARNING и DEBUG не считаются ошибками
    events = [
        Event(datetime(2026, 10, 18, 9, 0), "INFO", "api", "Ok"),
        Event(datetime(2026, 10, 18, 9, 1), "WARNING", "api", "Slow"),
        Event(datetime(2026, 10, 18, 9, 2), "DEBUG", "db", "Debug"),
    ]

    result = analyze(events)

    assert result[0] == 3
    assert result[1]["INFO"] == 1
    assert result[1]["WARNING"] == 1
    assert result[1]["DEBUG"] == 1
    assert result[2] == {"api": 2, "db": 1}
    assert result[3] == {}
    assert result[6] == []


def test_alphabetical_order():  # При одинаковом количестве ошибок
    # источники сортируются по алфавиту
    events = [
        Event(datetime(2026, 10, 18, 10, 0), "ERROR", "zebra", "A"),
        Event(datetime(2026, 10, 18, 10, 1), "ERROR", "alpha", "B"),
        Event(datetime(2026, 10, 18, 10, 2), "ERROR", "beta", "C"),
    ]

    result = analyze(events)

    assert result[6] == [
        ("alpha", 1),
        ("beta", 1),
        ("zebra", 1),
    ]


def test_generator_events():  # Анализатор принимает генератор, а не только список
    events = (
        Event(
            datetime(2026, 10, 18, 10, minute),
            "INFO",
            "api",
            "Message",
        )
        for minute in range(5)
    )

    result = analyze(events)

    assert result[0] == 5
    assert result[1]["INFO"] == 5
    assert result[2] == {"api": 5}
    assert result[3] == {}
    assert result[4] == datetime(2026, 10, 18, 10, 0)
    assert result[5] == datetime(2026, 10, 18, 10, 4)


def test_mixed_source_events():  # ERROR и обычные события одного источника
    events = [
        Event(datetime(2026, 10, 18, 10, 0), "INFO", "api", "Started"),
        Event(datetime(2026, 10, 18, 10, 1), "ERROR", "api", "Failed"),
        Event(datetime(2026, 10, 18, 10, 2), "WARNING", "api", "Slow"),
        Event(datetime(2026, 10, 18, 10, 3), "CRITICAL", "api", "Down"),
    ]

    result = analyze(events)

    assert result[0] == 4
    assert result[2] == {"api": 4}
    assert result[3] == {"api": 2}
    assert result[6] == [("api", 2)]
