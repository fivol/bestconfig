import os
from pathlib import Path
import typing as t

from bestconfig.source import Source
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
        return source.get('data')


class FileAdapter(AbstractAdapter):
    """Читает и пишет в файл"""

    @classmethod
    def get_dict(cls, source: Source) -> dict:
        filepath = source.get('filepath')
        assert isinstance(filepath, Path)
        filetype = cls._get_file_type(filepath)

        if filetype in cls.specific_parsers:
            parser = cls.specific_parsers[filetype]
        else:
            raise NotImplementedError('This file type does not supported yet %s' % filepath)
        return parser.read(str(filepath))

    # TODO добавить .env .cfg .ini
    """Обработчики файлов нужного типа"""
    specific_parsers = {
        'json': JsonParser,
        'yaml': YamlParser,
        'ini': IniParser,
        # same with .ini
        'cfg': IniParser,
        'env': EnvParser,
        'py': PyParser,
    }

    """Общепринятые названия и соответствующие им расширения"""
    file_types = {
        'env_file': 'env',
        '.env': 'env',
    }

    @classmethod
    def _get_file_type(cls, filepath: Path) -> t.Optional[str]:
        """Возвращает тип файла, обычно просто его расширение
        None если не найдено"""
        _, ext = os.path.splitext(filepath)
        filename = os.path.basename(filepath)

        ext = ext.strip('.')
        if ext in cls.specific_parsers:
            return ext

        if filename in cls.file_types:
            return cls.file_types[filename]

        return None
