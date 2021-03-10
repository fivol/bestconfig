import os
import traceback
from abc import abstractmethod, ABCMeta
import typing as t
from enum import Enum, auto
from pathlib import Path
import json
import yaml
from environs import Env

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
        else:
            raise ValueError('Unknown source type %s' % type(value))

        self.manual = manual


class Config:
    """
    Основной класс, является частью публичного
    интерфейса библиотеки.

    Пример использования:

    from bestconfig import Config
    config = Config()
    print(config.limit)
    """

    def __new__(cls, *args, exclude_default=False, raise_on_absent=False, exclude: list = None):
        sources = cls._get_sources(*args, exclude_default=exclude_default, exclude=exclude)
        # Передаем файл, из которого был совершен вызов Config()
        # в объекте traceback.extract_stack, последний вызов это данная функция, а перед ним, вызывающая
        caller_path = traceback.extract_stack()[-2][0]
        sources = SourcesFilter.filter(sources, caller_path=caller_path)
        return

    """Начало и конец списка источников конфигов, те, что ближе к концу 
    кри коллизии перезаписывают более ранние"""
    _sources_begin = generate_sources(applicant_files, supported_extensions)
    _sources_end = ['.env', 'env_file', Source.env]

    @classmethod
    def _get_sources(cls, *args, exclude_default, exclude: list) -> t.List[Source]:
        """Дополняет переданные пользователем источники (файлы) стандартными"""
        exclude_set = set(exclude)
        sources = []
        if not exclude_default:
            sources += [source_name for source_name in cls._sources_begin if source_name not in exclude_set]
        sources += args
        if not exclude_default:
            sources += [source_name for source_name in cls._sources_end if source_name not in exclude_set]

        return [Source(source) for source in sources]


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


class SourcesFilter:
    """Делает preprocessing входных источников,
    превращает их в реальные пути к файлам, удаляет невалид и прочее"""

    @classmethod
    def filter(cls, sources: t.List[Source], caller_path: str) -> t.List[Source]:
        """Основной метод класса
        Заменяет названия файлов на реальные пути в формате Path"""
        clear_sources = []
        scanner = FilesScanner(caller_path=caller_path)
        for source in sources:
            if SourceType.FILE == source.source_type:
                clear_sources += scanner.find_all_files(source.data['filename'])
            else:
                clear_sources.append(source)

        return clear_sources


class FilesScanner:
    """
    Задача класса находить файлы конфигурации
    в директориях проекта
    """

    def __init__(self, caller_path: str):
        self._root_path = Path(os.getcwd())
        self._caller_path = caller_path

    def find_all_files(self, filename: str) -> t.List[Path]:
        """
        Принимает название или часть названия файла
        и возвращает список подходящих в порядке
        более глубокой вложенности
        """
        paths = []
        depth_limit = 4
        curr_dirname = Path(self._caller_path)
        for i in range(depth_limit):
            path = self._get_path(str(curr_dirname), filename)
            if path:
                paths.append(path)
            if curr_dirname == self._root_path:
                break

            curr_dirname = curr_dirname.parent

        # Самый последний, наиболее глубокий в файловой структуре
        return paths[::-1]

    @classmethod
    def _get_path(cls, dir_path: str, filename: str) -> t.Optional[Path]:
        """Проверяет в данной директории наличие файла
        по паттерну filename, возвращает None при отсутствии
        и Path() если существует"""
        dir_path = Path(dir_path)
        if not dir_path.exists():
            return None
        files = os.listdir(dir_path)
        for file in files:
            filepath = os.path.join(dir_path, file)
            if filename in filepath:
                return Path(filepath)

        return None


class FileIOException(Exception):
    """Ошибка операции с файлом, например недоступен для записи"""
    pass


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


class AbstractFileParser(metaclass=ABCMeta):
    """
    Родительский класс для парсеров конфигов различных форматов
    """

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


class YamlParser(AbstractFileParser):
    """Парсит файлы с расширением .yaml"""
    extension = 'yaml'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            return yaml.load(file)


class JsonParser(AbstractFileParser):
    """Парсит файлы с расширением .json"""
    extension = 'json'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            return json.load(file)


class EnvParser(AbstractFileParser):
    """Читает .env файлы и подобные ему
    Файл должен быть в формате VAR_NAME=VAR_VALUE"""

    extension = 'env'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            return yaml.load(file)


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
    }


class ConfigSourceAdapter:
    """
    Предоставляет ряд универсальных методов для работы с источником конфига.
    Инкапсулирует реальный доступ к источнику
    Парсинг, модификация, доступ к полям и прочее
    """

    def __init__(self, source: Source):
        self._source = source
        self._adapter = self._adapters_dict[source.source_type]

    def get_dict(self):
        return self._adapter.get_dict(self._source)

    _adapters_dict = {
        SourceType.ENV: EnvAdapter,
        SourceType.FILE: FileAdapter,
        SourceType.DICT: DictAdapter
    }


if __name__ == '__main__':
    config = Config('file')
