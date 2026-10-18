from datetime import datetime

import pytest

from streamstats.errors import (
    InvalidEventError,
    InvalidSourceError,
    InvalidTimestampError,
)
from streamstats.parsers import make_event, parse_csv, parse_jsonl


def test_jsonl_valid(tmp_path):  # Корректный JSONL
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"ERROR","source":"api","message":"Connection failed"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(path))

    assert len(events) == 1
    assert events[0].timestamp == datetime(2026, 10, 18, 10, 0)
    assert events[0].level == "ERROR"
    assert events[0].source == "api"
    assert events[0].message == "Connection failed"


def test_csv_valid(tmp_path):  # Корректный CSV
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T11:00:00,INFO,server,Started\n"
        "2026-10-18T11:05:00,WARNING,db,Slow query\n",
        encoding="utf-8",
    )

    events = list(parse_csv(path))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[0].source == "server"
    assert events[1].level == "WARNING"
    assert events[1].source == "db"
    assert events[1].message == "Slow query"


def test_empty_jsonl(tmp_path):  # Пустой JSONL
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    assert list(parse_jsonl(path)) == []


def test_empty_csv(tmp_path):  # CSV только с заголовком
    path = tmp_path / "empty.csv"
    path.write_text("timestamp,level,source,message\n", encoding="utf-8")

    assert list(parse_csv(path)) == []


def test_invalid_level_jsonl(tmp_path):  # Некорректный уровень в JSONL, без пропуска
    path = tmp_path / "invalid.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"BANANA","source":"api","message":"Test"}\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(path))


def test_invalid_timestamp_csv(tmp_path):  # Некорректная дата в CSV, без пропуска
    # парсер оборачивает ошибку в InvalidEventError.
    path = tmp_path / "invalid.csv"
    path.write_text(
        "timestamp,level,source,message\n" "not-a-date,INFO,api,Test\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_csv(path))


def test_invalid_source():  # Некорректный источник в make_event
    row = {
        "timestamp": "2026-10-18T10:00:00",
        "level": "INFO",
        "source": "   ",
        "message": "Test",
    }

    with pytest.raises(InvalidSourceError):
        make_event(row, 1)


def test_timestamp_wrong_type():  # Некорректный тип timestamp в make_event
    row = {
        "timestamp": 123,
        "level": "INFO",
        "source": "api",
        "message": "Test",
    }

    with pytest.raises(InvalidTimestampError):
        make_event(row, 1)


def test_jsonl_skip_invalid(tmp_path):  # Пропуск неверного уровня в JSONL
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"api","message":"OK"}\n'
        '{"timestamp":"2026-10-18T10:01:00",'
        '"level":"BANANA","source":"api","message":"Wrong"}\n'
        '{"timestamp":"2026-10-18T10:02:00",'
        '"level":"ERROR","source":"db","message":"Failed"}\n',
        encoding="utf-8",
    )

    skipped = {"count": 0}
    events = list(parse_jsonl(path, skip_invalid=True, skipped=skipped))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].level == "ERROR"
    assert skipped["count"] == 1


def test_csv_skip_invalid(tmp_path):  # Пропуск неверной даты в CSV
    path = tmp_path / "events.csv"
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T10:00:00,INFO,api,OK\n"
        "wrong-date,ERROR,db,Bad date\n"
        "2026-10-18T10:02:00,WARNING,worker,Slow\n",
        encoding="utf-8",
    )

    skipped = {"count": 0}
    events = list(parse_csv(path, skip_invalid=True, skipped=skipped))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[1].level == "WARNING"
    assert skipped["count"] == 1


def test_broken_jsonl(tmp_path):  # Повреждённый JSON
    path = tmp_path / "broken.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"api","message":"Broken"\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(path))


def test_empty_message(tmp_path):  # пустое сообщение
    path = tmp_path / "unicode.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"сервер","message":"Привет"}\n'
        '{"timestamp":"2026-10-18T10:01:00",'
        '"level":"DEBUG","source":"api","message":""}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(path))

    assert len(events) == 2
    assert events[0].source == "сервер"
    assert events[0].message == "Привет"
    assert events[1].message == ""
