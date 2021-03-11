import os
from abc import abstractmethod
from pathlib import Path

from bestconfig.config import Source
from bestconfig.file_parsers import *


class AbstractAdapter(metaclass=ABCMeta):

    @classmethod
    @abstractmethod
    def get_dict(cls, source: Source) -> dict:
        """Возвращает словарь с конфигами,
        необходимые параметры находятся в source"""
        pass


class EnvAdapter(AbstractAdapter):
    """Адаптер для доступа к переменным окружения"""

    @classmethod
    def get_dict(cls, source: Source) -> dict:
        return dict(os.environ)


class DictAdapter(AbstractAdapter):
    """Получение конфига из python dict"""

    @classmethod
    def get_dict(cls, source: Source) -> dict:
        return source.data


class FileAdapter(AbstractAdapter):
    """Читает и пишет в файл"""

    @classmethod
    def get_dict(cls, source: Source) -> dict:
        filepath = source.data.get('filepath')
        assert isinstance(filepath, Path)
        _, extension = os.path.splitext(filepath)
        filename = os.path.basename(filepath)
        if extension in cls.specific_parsers:
            parser = cls.specific_parsers[extension]
        else:
            raise NotImplementedError('This file type does not supported yet %s' % filename)
        return parser.read(str(filepath))

    # TODO добавить .env .cfg .ini
    specific_parsers = {
        'json': JsonParser,
        'yaml': YamlParser,
        'ini': IniParser
    }
