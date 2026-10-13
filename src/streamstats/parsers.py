from datetime import datetime
from .models import Event
import csv

def parse_csv(path):
    with open(path, encoding="utf-8", newline="") as file: #автоматически закрывает за собой файл, указывает кодировку текста, добавляет режим обработки
        reader = csv.reader(file)
        next(reader) #скипаем заголовок  
        for row in (reader): 
            print(parse(row))


def parse(row):
    time = row[0]
    level = row[1]
    source = row[2]
    time = datetime.fromisoformat(time)
    event = Event(time, level, source)
    return event

