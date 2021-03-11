import os
import traceback
import typing as t
from pathlib import Path

from bestconfig.adapters import EnvAdapter, FileAdapter, DictAdapter
from bestconfig.config_provider import ConfigProvider
from bestconfig.source import Source, SourceType

supported_extensions = ['json', 'yaml', 'ini', 'cfg', 'env']
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


class Config:
    """
    Основной класс, является частью публичного
    интерфейса библиотеки.

    Пример использования:

    from bestconfig import Config
    config = Config()
    print(config.limit)
    """

    def __new__(cls, *args, exclude_default=False, raise_on_absent=False, exclude: list = None) -> ConfigProvider:
        # Добавить значения по умолчанию
        sources = cls._get_sources(*args, exclude_default=exclude_default, exclude=exclude or set())
        # Передаем файл, из которого был совершен вызов Config()
        # в объекте traceback.extract_stack, последний вызов это данная функция, а перед ним, вызывающая
        caller_path = traceback.extract_stack()[-2][0]
        sources = SourcesFilter.filter(sources, caller_path=caller_path)
        aggregator = ConfigAggregator(sources)
        config_dict = aggregator.to_dict()
        return ConfigProvider(config_dict)

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
                found_files = scanner.find_all_files(source.data['filename'])
                for filename in found_files:
                    clear_sources.append(Source(filename))
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
        curr_dirname = os.path.dirname(self._caller_path)
        curr_dirname = Path(curr_dirname)
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


class ConfigSourceAdapter:
    """
    Предоставляет ряд универсальных методов для работы с источником конфига.
    Инкапсулирует реальный доступ к источнику
    Парсинг, модификация, доступ к полям и прочее
    """

    def __init__(self, source: Source):
        self._source = source
        self._adapter = self._adapters_dict[source.source_type]

    def get_dict(self) -> dict:
        return self._adapter.get_dict(self._source)

    _adapters_dict = {
        SourceType.ENV: EnvAdapter,
        SourceType.FILE: FileAdapter,
        SourceType.DICT: DictAdapter
    }


class ConfigAggregator:
    """Превращает сырые словари из файлов и других источников
     в итоговый набор конфигов для пользования"""

    def __init__(self, source: t.List[Source]):
        self._sources = source

    def to_dict(self) -> dict:
        """Возвращает готовый итоговый словарь, содержащий
        все необходимые данные (переменные конфигурации)"""
        return self._combine_sources()

    @classmethod
    def _extract_source(cls, source) -> dict:
        """Возвращает соответствующий источнику словарь данных"""
        adapter = ConfigSourceAdapter(source)
        return adapter.get_dict()

    def _combine_sources(self) -> dict:
        """Возвращает общий для всех источников словарь"""
        data = {}
        for source in self._sources:
            data.update(self._extract_source(source))

        return data
