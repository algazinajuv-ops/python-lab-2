from datetime import datetime


class Event:  # создали класс
    def __init__(self, timestamp: datetime, level: str, source: str, message: str):
        self.timestamp = timestamp  # сохранить переданное значение внутри переменной
        self.level = level
        self.source = source
        self.message = message
