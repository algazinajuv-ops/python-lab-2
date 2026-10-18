import json
import subprocess
import sys


def run_cli(*args):  # функция для запуска программы через терминал
    return subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "streamstats", *map(str, args)],
        capture_output=True,  # сохраняем вывод программы
        text=True,  # получаем строки, а не байты
        encoding="utf-8",
        check=False,
    )


def test_cli_help():  # проверяем справку CLI
    result = run_cli("--help")

    assert result.returncode == 0
    assert "analyze" in result.stdout


def test_cli_jsonl(tmp_path):  # проверяем анализ корректного JSONL
    path = tmp_path / "events.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"api","message":"Started"}\n'
        '{"timestamp":"2026-10-18T10:01:00",'
        '"level":"ERROR","source":"db","message":"Failed"}\n',
        encoding="utf-8",
    )

    result = run_cli("analyze", path, "--format", "jsonl")

    assert result.returncode == 0

    report = json.loads(result.stdout)  # преобразуем JSON в словарь

    assert report["total"] == 2
    assert report["skipped"] == 0
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1
    assert report["sources"] == {"api": 1, "db": 1}
    assert report["error_sources"] == {"db": 1}
    print(result.stdout)


def test_cli_csv(tmp_path):  # проверяем анализ корректного CSV
    path = tmp_path / "events.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-18T09:00:00,WARNING,api,Slow\n"
        "2026-10-18T09:05:00,CRITICAL,db,Crash\n",
        encoding="utf-8",
    )

    result = run_cli("analyze", path, "--format", "csv")

    assert result.returncode == 0

    report = json.loads(result.stdout)

    assert report["total"] == 2
    assert report["skipped"] == 0
    assert report["levels"]["WARNING"] == 1
    assert report["levels"]["CRITICAL"] == 1
    assert report["sources"] == {"api": 1, "db": 1}
    assert report["error_sources"] == {"db": 1}


def test_cli_skip_invalid(tmp_path):  # проверяем пропуск неверной записи
    path = tmp_path / "invalid.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"api","message":"OK"}\n'
        '{"timestamp":"2026-10-18T10:01:00",'
        '"level":"BANANA","source":"api","message":"Wrong"}\n'
        '{"timestamp":"2026-10-18T10:02:00",'
        '"level":"ERROR","source":"db","message":"Failed"}\n',
        encoding="utf-8",
    )

    result = run_cli("analyze", path, "--format", "jsonl", "--skip-invalid")

    assert result.returncode == 0

    report = json.loads(result.stdout)

    assert report["total"] == 2
    assert report["skipped"] == 1
    assert report["levels"]["INFO"] == 1
    assert report["levels"]["ERROR"] == 1
    assert report["error_sources"] == {"db": 1}
    assert "invalid.jsonl:2" in result.stderr


def test_cli_output_file(tmp_path):  # проверяем сохранение JSON-отчёта
    input_path = tmp_path / "events.jsonl"
    output_path = tmp_path / "result.json"

    input_path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"INFO","source":"api","message":"Hello"}\n',
        encoding="utf-8",
    )

    result = run_cli(
        "analyze",
        input_path,
        "--format",
        "jsonl",
        "--output",
        output_path,
    )

    assert result.returncode == 0
    assert output_path.exists()  # проверяем, что файл появился

    report = json.loads(output_path.read_text(encoding="utf-8"))

    assert report["total"] == 1
    assert report["skipped"] == 0
    assert report["sources"] == {"api": 1}


def test_cli_missing_file(tmp_path):  # проверяем несуществующий файл
    path = tmp_path / "nonexistent.jsonl"

    result = run_cli("analyze", path, "--format", "jsonl")

    assert result.returncode == 2
    assert "Ошибка" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_invalid_event(tmp_path):  # неверная запись без skip-invalid
    path = tmp_path / "invalid.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-18T10:00:00",'
        '"level":"BANANA","source":"api","message":"Wrong"}\n',
        encoding="utf-8",
    )

    result = run_cli("analyze", path, "--format", "jsonl")

    assert result.returncode == 2
    assert "invalid.jsonl:1" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_invalid_format():  # проверяем неподдерживаемый формат
    result = run_cli("analyze", "events.jsonl", "--format", "xml")

    assert result.returncode == 2
    assert "invalid choice" in result.stderr
