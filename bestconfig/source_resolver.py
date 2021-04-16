import os
import traceback
import typing as t
import warnings
from pathlib import Path

from bestconfig.adapters import EnvAdapter, FileAdapter, DictAdapter

from bestconfig.source import Source, TargetType, SourceType


class SourceResolver:
    """
    Получает сырые данные:
    1. Названия файлов
    2. python словари
    3. Source.env, как указание на переменные окружения
    И превращает их в готовые словари
    """

    def __init__(self, caller_path: str):
        self._caller_path = caller_path

    def resolve(self, target: TargetType) -> dict:
        sources = SourceFilter.transform(target, caller_path=self._caller_path)
        aggregator = ConfigAggregator(sources)
        config_dict = aggregator.to_dict()
        return config_dict

    def resolve_all(self, targets: t.List[TargetType]) -> dict:
        data = {}
        for target in targets:
            data.update(self.resolve(target))

        return data


class SourceFilter:
    """Делает preprocessing входных источников,
    превращает их в реальные пути к файлам, удаляет не валид и прочее"""

    @staticmethod
    def _source_from_target(target: TargetType) -> Source:
        """Преобразование пользовательского типа
        в класс Source, отображающий универсальный источник данных"""
        if target == Source.env:
            source = Source(SourceType.ENV)
        elif isinstance(target, dict):
            source = Source(SourceType.DICT)
            source.set('data', target)
        elif isinstance(target, str):
            source = Source(SourceType.FILE)
            source.set('filename', target)
        elif isinstance(target, Path):
            source = Source(SourceType.FILE)
            source.set('filename', str(target))
        else:
            raise ValueError('Unknown source type %s' % type(target))

        return source

    @classmethod
    def transform(cls, target: TargetType, caller_path: str) -> t.List[Source]:
        """Основной метод класса
        Преобразует TargetType -> Source
        То есть названия, алиасы и прочее превращаются в структурированные
        данные, возможно в список, если по паттерну было найдено несколько
        файлов
        """
        clear_sources = []
        scanner = FilesScanner(caller_path=caller_path)
        source = cls._source_from_target(target)

        if SourceType.FILE == source.source_type:
            found_files = scanner.find_all_files(source.get('filename'))
            for filename in found_files:
                new_source = Source(SourceType.FILE)
                new_source.set('filepath', filename)
                clear_sources.append(new_source)
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

    @staticmethod
    def get_caller_path():
        """Возвращает файл, в котором была вызвана
        функция, которая вызвала эту"""
        return traceback.extract_stack()[-3][0]

    def find_all_files(self, filename: str) -> t.List[Path]:
        """
        Принимает название или часть названия файла
        и возвращает список подходящих в порядке
        более глубокой вложенности
        """
        paths = []
        curr_dirname = os.path.dirname(self._caller_path)
        curr_dirname = Path(curr_dirname)
        for i in range(self._depth_limit):
            path = self._get_path(curr_dirname, filename)
            if path:
                paths.append(path)
            if curr_dirname == self._root_path:
                break

            curr_dirname = curr_dirname.parent

        passed_file = Path(filename)
        if passed_file.is_file() and passed_file not in paths:
            paths.append(passed_file)

        # Самый последний, наиболее глубокий в файловой структуре
        return list(reversed(paths))

    @classmethod
    def _get_path(cls, dir_path: Path, filename: str) -> t.Optional[Path]:
        """Проверяет в данной директории наличие файла
        по паттерну filename, возвращает None при отсутствии
        и Path() если существует"""
        if not dir_path.exists():
            return None

        filepath = os.path.join(dir_path, filename)
        # Обрабатывает случаи вида /hello/../other
        filepath = Path(os.path.abspath(filepath))
        if not filepath.is_file():
            return None
        return filepath

    _depth_limit = 4


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
        data_dict = adapter.get_dict()
        return data_dict or {}

    def _combine_sources(self) -> dict:
        """Возвращает общий для всех источников словарь"""
        data = {}
        for source in self._sources:
            data.update(self._extract_source(source))

        return data
