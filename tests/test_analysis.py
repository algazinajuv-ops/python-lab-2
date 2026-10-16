from datetime import datetime

from streamstats.analysis import analyze
from streamstats.models import Event


def test_empty_events():
    result = analyze([])

    assert result[0] == 0 # проверяет истинно ли условие
    assert result[2] == {}
    assert result[3] == {}
    assert result[4] is None
    assert result[5] is None
    assert result[6] == []

def test_two_events():
    events = [
    Event(datetime(2026, 10, 16, 10, 0), "INFO", "api"),
    Event(datetime(2026, 10, 16, 10, 5), "ERROR", "db"),
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
    assert result[2]["api"] == 1
    assert result[2]["db"]==1
    assert result[3] == {"db": 1}
    assert result[4] == datetime(2026, 10, 16, 10, 0)
    assert result[5] == datetime(2026, 10, 16, 10, 5)
    assert result[6] == [("db", 1)]



def test_unsorted_events():
    events = [
        Event(datetime(2026, 10, 16, 15, 0), "INFO", "api"),
        Event(datetime(2026, 10, 16, 9, 0), "ERROR", "db"),
        Event(datetime(2026, 10, 16, 12, 0), "WARNING", "worker"),
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
    assert result[2] == {
            "api": 1,
            "db": 1,
            "worker": 1,
        }
    assert result[3] == {"db": 1}
    assert result[4] == datetime(2026, 10, 16, 9, 0)
    assert result[5] == datetime(2026, 10, 16, 15, 0)
    assert result[6] == [("db", 1)]


def test_tpo5_events():
    counts = {
    "api": 3,
    "db": 5,
    "cache": 3,
    "worker": 2,
    "auth": 1,
    "network": 4,
    }
    events = []
    for source, count in counts.items(): #генерим 18 событий
        for _ in range(count):
            events.append(
                Event(datetime(2026, 10, 16, 10, 0), "ERROR", source)
            )
    result = analyze(events)
    assert result[0] == 18
    assert result[1] == {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 18,
        "CRITICAL": 0,
    }
    assert result[2] == {
        "api": 3,
        "db": 5,
        "cache": 3,
        "worker": 2,
        "auth": 1,
        "network": 4,
    }
    assert result[3] == {
        "api": 3,
        "db": 5,
        "cache": 3,
        "worker": 2,
        "auth": 1,
        "network": 4,
    }
    assert result[4] == datetime(2026, 10, 16, 10, 0)
    assert result[5] == datetime(2026, 10, 16, 10, 0)
    assert result[6] ==  [
        ("db", 5),
        ("network", 4),
        ("api", 3),
        ("cache", 3),
        ("worker", 2),
    ]



