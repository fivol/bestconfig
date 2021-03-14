from enum import Enum, auto
from pathlib import Path
import typing as t


class SourceType(Enum):
    """Тип переданного в Config() источника """
    ENV = auto()
    DICT = auto()
    FILE = auto()


"""
Тип объекта, передаваемого пользователем для инициализации
словаря конфигурации, это может быть 
1. Название файла (полный пусть, часть пути, относительный путь)
2. Непосредственно словарь
"""
TargetType = t.Union[str, dict, Path]


class Source:
    """
    Класс для хранения промежуточных результатов
    получения итогового словаря из target.
    Соглашение о данных
    filename: str. Путь до файла, относительный или абсолютный
    filepath: Path. Абсолютный путь до файла
    data: dict. Словарь конфигов
    """
    env = '__ENV__'

    def __init__(self, source_type: SourceType):
        """
        :param source_type: тип источника
        """

        # dict в котором хранятся данные, характеризующие источник
        self._data = {}
        self.source_type = source_type

    def set(self, item: str, value):
        self._data[item] = value

    def get(self, item: str):
        return self._data[item]

    def __repr__(self):
        return f'Source({self.source_type})'
