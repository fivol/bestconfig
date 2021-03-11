from enum import Enum, auto
from pathlib import Path


class SourceType(Enum):
    """Тип переданного в Config() источника """
    ENV = auto()
    DICT = auto()
    FILE = auto()


class Source:
    """Класс обертка над источникоми конфигов,
    например:
     - Source.env - указывает на переменные окружения
     TODO: Дописать примеры использования
     """
    env = '__ENV__'

    def __init__(self, value, manual=False):
        """
        :param value:
        :param manual: True, если данный источник указал пользователь вручную
        False, если взято из настроек по умолчанию
        """
        # TODO точка роста, сюда можно добавить другие источники

        # dict в котором хранятся данные, характеризующие источник
        self.data = {}

        if value == self.env:
            self.source_type = SourceType.ENV
        elif isinstance(value, dict):
            self.source_type = SourceType.DICT
            self.data = value
        elif isinstance(value, str):
            self.source_type = SourceType.FILE
            self.data['filename'] = value
        elif isinstance(value, Path):
            self.source_type = SourceType.FILE
            self.data['filepath'] = value
        else:
            raise ValueError('Unknown source type %s' % type(value))

        self.manual = manual

    def __repr__(self):
        return f'Source({self.data})' if self.data else f'Source(type={self.source_type})'
