from datetime import *

class Event: #создали класс
    def __init__(self, time: datetime, level:str, source:str): 
        self.time = time #сохранить переданное значение внутри переменной
        self.level = level 
        self.source = source 