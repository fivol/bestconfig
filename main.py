import os
from abc import abstractmethod, ABCMeta
import typing as t
from pathlib import Path

supported_extensions = ['json', 'yaml', 'ini', 'cfg']
applicant_files = ['config', 'conf', 'setting', 'settings', 'configuration']


def generate_sources(files: t.List[str], extensions: t.List[str]) -> t.List[str]:
    """Генерирует всевозможные названия файлов
    на основе предоставленных претендентов на названия и расширения"""
    return list(sum(
        [
            [f'{filename}.{ext}' for ext in extensions]
            for filename in files
        ],
        []
    ))


class Source:
    """Класс обертка над источникоми конфигов,
    например:
     - Source.env - указывает на переменные окружения
     TODO: Дописать примеры использования
     """
    env = '__ENV__'

    def __init__(self, filename: str):
        pass


class Config:
    """
    Основной класс, является частью публичного
    интерфейса библиотеки.

    Пример использования:

    from bestconfig import Config
    config = Config()
    print(config.limit)
    """

    def __new__(cls, *args, exclude_default=False, raise_on_absent=False, exclude_files: list = None):
        pass

    """Начало и конец списка источников конфигов"""
    _sources_end = [Source.env]
    _sources_begin = generate_sources(applicant_files, supported_extensions)


"""Тип, которым может быть значение конфига"""
ConfigType = t.Union[str, int, float, bool, dict, list]


class ConfigProvider:
    """
    Основной класс, с которым имеет дело пользователь
    после создания конфига.
    Предоставляет универсальный интерфейс для хранящихся данных
    Пример:
    config = Config()
    assert isinstance(config, ConfigProvider)
    print(config.logger.format)
    print(config['logger.format'])
    print(config['logger']['format'])
    print(config.logger['format'])
    print(config.get('logger'))
    """

    def __init__(self, data: dict):
        self._data: dict = data
        self._modified: bool = False

    @classmethod
    def _create_object(cls, data: dict):
        obj = object.__new__(cls)
        obj.__init__(data)
        return obj

    def __new__(cls, data: ConfigType):
        if isinstance(data, dict):
            return cls._create_object(data)
        return data

    def get(self, item, default_value=None, raise_absent=False) -> ConfigType:
        """
        Обращается к self._data и возвращает собственный экземпляр, если значение dict
        в противном случае само значение

        attr_name = config.get('attr_name', 123)
        """
        if item in self._data:
            return self.__new__(self.__class__, self._data['item'])

        if raise_absent:
            raise KeyError

        return default_value

    def __getattr__(self, item):
        """
        attr_name = config.attr_name
        """
        return self.get(item)

    def __getitem__(self, item):
        """
        attr_name = config['attr_name']
        """
        return ConfigProvider(self._data[''])

    def set(self, item: str, value: ConfigType):
        """Устанавливает значение по ключу"""
        self._modified = True
        self._data[item] = value


class ConfigFileAdapter:
    """
    Отражает реальный файл конфига, предоставляет ряд методов для работы с ним:
    парсинг, модификация, доступ к полям и прочее
    """
    pass


class FilesScanner:
    """
    Задача класса находить файлы конфигурации
    в директориях проекта
    """

    def __init__(self, caller_path):
        self._root_path = Path(os.getcwd())
        self._caller_path = caller_path

    def find_file(self, filename: str) -> t.Optional[Path]:
        return


class FileIOException(Exception):
    """Ошибка операции с файлом, например недоступен для записи"""
    pass


class AbstractFileParser:
    """
    Родительский класс для парсеров конфигов различных форматов
    """
    __metaclass__ = ABCMeta

    """
    Расширение файла, которое обрабатывает данный класс,
    должно переопределяться в наследниках
    """
    extension = ''

    @classmethod
    @abstractmethod
    def read(cls, filepath: str) -> dict:
        """
        :param filepath: полный путь до файла соответствующего типа (extension)
        :return: считанные из файла данные в виде python словаря
        Возбуждает FileNotFoundError при отсутствии файла
        """
        pass

    @classmethod
    @abstractmethod
    def write(cls, filepath: str, data: dict) -> None:
        """
        Записывает dict в файл соответствующего типа
        :param filepath: полный путь до файла
        :param data: python dict, который нужно записать в файл
        :return: Может кидать ошибку FileIOException при ошибки записи
        """


class YamlParser(AbstractFileParser):
    """Парсит файлы с расширением .yaml"""
    extension = 'yaml'

    @classmethod
    def read(cls, filepath: str) -> dict:
        pass

    @classmethod
    def write(cls, filepath: str, data: dict) -> None:
        pass


class JsonParser(AbstractFileParser):
    """Парсит файлы с расширением .json"""
    extension = 'json'

    @classmethod
    def read(cls, filepath: str) -> dict:
        pass

    @classmethod
    def write(cls, filepath: str, data: dict) -> None:
        pass


if __name__ == '__main__':
    config = Config('file')
