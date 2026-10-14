from datetime import datetime
from .models import Event
import csv
import json
from .errors import InvalidEventError, InvalidSourceError, InvalidTimestampError, StreamStatsError

def parse_csv(path, skip_invalid = False):
    with open(path, encoding="utf-8", newline="") as file: #автоматически закрывает за собой файл, 
                                                            #указывает кодировку текста, добавляет режим обработки
        reader = csv.DictReader(file) 

        for number, row in enumerate(reader, start= 2): #нумерация
            try:
                yield(make_event(row, number)) #выдает и приостанавливает до след запроса
            except StreamStatsError:
                if skip_invalid:
                    continue #продолжаем
                else:
                    raise #запускаем ошибку

def parse_jsonl(path, skip_invalid = False):
    with open(path, encoding='utf-8', newline="") as file:
        for number, row in enumerate(file, start=1): #старт с 1 потому что в джсон нет загаловка
            try:
                row = json.loads(row)
                if not(isinstance(row, dict)):
                    raise InvalidEventError(f"Неверная запись в {number} строке")
                yield(make_event(row, number))
            except (StreamStatsError, json.JSONDecodeError): #проверить еще и ошибку синтаксиса файла
                if skip_invalid:
                    continue
                else: raise
            

allowed_levels = {
    "DEBUG",            #разрешенные уровни
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}
def make_event(row: dict[str, str], number: int):
    time = row.get("time")  #вычленяем значение
    level = row.get('level')
    source = row.get("source")
    if level not in allowed_levels:
        raise InvalidEventError(f"Недопустимый уровень события в {number} строке") 
    if not time:
        raise InvalidTimestampError(f"Отсутствует время в {number} строке")
    if not source:
        raise InvalidSourceError(f"Отсутствует источник в {number} строке")
    try:
        time = datetime.fromisoformat(time)  #делаем нужный формат времени
    except ValueError:
        raise InvalidTimestampError(f"Некоректное значение времени в {number} строке")
    event = Event(time, level, source)
    return event



