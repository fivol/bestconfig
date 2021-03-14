import typing as t
from bestconfig.config_provider import ConfigProvider
from bestconfig.source import Source, TargetType
from bestconfig.source_resolver import SourceResolver, FilesScanner

supported_extensions = ['json', 'yaml', 'ini', 'cfg', 'env']
applicant_files = ['config', 'conf', 'setting', 'settings', 'configuration']


def generate_targets(files: t.List[str], extensions: t.List[str]) -> t.List[str]:
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
        targets = cls._get_targets(*args, exclude_default=exclude_default, exclude=exclude or set())
        # Передаем файл, из которого был совершен вызов Config()
        # в объекте traceback.extract_stack, последний вызов это данная функция, а перед ним, вызывающая
        resolver = SourceResolver(caller_path=FilesScanner.get_caller_path())
        # Преобразует все цели в один словарь
        config_dict = resolver.resolve_all(targets)
        return ConfigProvider(config_dict)

    """Начало и конец списка источников конфигов, те, что ближе к концу 
    при коллизии перезаписывают более ранние"""
    _targets_begin = generate_targets(applicant_files, supported_extensions)
    _targets_end = ['.env', 'env_file', Source.env]

    @classmethod
    def _get_targets(cls, *args, exclude_default, exclude: list) -> t.List[TargetType]:
        """Дополняет переданные пользователем источники (файлы) стандартными"""
        exclude_set = set(exclude)
        targets = []
        if not exclude_default:
            targets += [target for target in cls._targets_begin if target not in exclude_set]
        targets += args
        if not exclude_default:
            targets += [target for target in cls._targets_end if target not in exclude_set]

        return targets

