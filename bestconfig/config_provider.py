from warnings import warn
import inspect
from bestconfig.converters import *
from bestconfig.source_resolver import SourceResolver, FilesScanner
from bestconfig.source import TargetType

"""Тип, которым может быть значение конфига"""
ConfigType = t.Union[str, int, float, bool, dict, list]

"""
Используется по умолчанию, при
config.get()
Может быть переопределен параметром 'cast'
"""
default_converter = UniversalConverter()


class ConfigProvider(dict):
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
        super().__init__(data)

    def get(self, item: str, default_value=None, raise_absent=False,
            cast: t.Optional[AbstractConverter] = default_converter) -> ConfigType:
        """
        Обращается к self._data и возвращает собственный экземпляр, если значение dict
        в противном случае само значение

        attr_name = config.get('attr_name', 123)

        :param item: ключ, значение по которому нужно вернуть
        :param default_value: при отсутствии ключа, возвращается оно
        :param raise_absent: если ключа не существует, кинуть KeyError,
        в противном случает вернуть None
        :param cast: наследник класса AbstractConverter,
        если передан, возвращается cast.cast(value)
        :return: значение по ключу, None или KeyError
        """
        assert isinstance(item, str), 'Key must be str, not %s' % type(item)

        try:
            # Обработка случая config.get('key.other')
            value = self._unsafe_access_key(item)
            # Возвращаем словарь в виде класса ConfigProvider
            if isinstance(value, dict):
                return self.__class__(value)

            # Преобразуем объект в соответствии с переданным в параметрах cast
            if cast:
                return cast.cast(value)
            return value
        except KeyError:
            if raise_absent:
                raise KeyError

        return default_value

    def get_raw(self, item: str):
        """Возвращает значение по ключу, не изменяя его
        Такое, какое было считано из файла"""
        return self.get(item, cast=None)

    def contains(self, item: str):
        return self.get(item) is not None

    def assert_contains(self, item: str):
        """Бросает исключение KeyError, если ключ не найден"""
        self.get(item, raise_absent=True)

    def set(self, item: str, value: ConfigType):
        """Устанавливает значение по ключу"""
        if not item:
            warn('Использование пустой строки в качестве ключа', UserWarning)
        self[item] = value

    def to_dict(self) -> dict:
        """Возвращает весь конфигурационные словарь, содержащий имеющиеся данные
        Эквивалентно dict(config)"""
        return dict(self)

    def insert(self, target: TargetType):
        """
        Добавляет в основное хранилище новые данные
        по указанию target (то же самое, что аргумент в Config())
        :param target: имя файла или словарь
        """
        resolver = SourceResolver(FilesScanner.get_caller_path())
        new_data = resolver.resolve(target)
        self.update(new_data)

    def update_from_locals(self):
        """Обновляет словарь отфильтрованными локальными переменными
        из вызвавшего функцию контекста.
        Переменные только типов (str, int, float, dict, list)
        будут учтены
        """
        config_types = (str, int, float, dict, list)

        def is_config_var(name, value):
            if not isinstance(value, config_types):
                return False
            if name.startswith('__'):
                return False
            if isinstance(value, self.__class__):
                return False
            return True

        local_vars = inspect.currentframe().f_back.f_locals
        data = {
            key: value for key, value in local_vars.items()
            if is_config_var(key, value)
        }
        self.insert(data)

    def int(self, item: str) -> t.Optional[int]:
        """ config.int('limit') -> 45 """
        return self.get(item, cast=SimpleConverter(int))

    def float(self, item: str) -> t.Optional[float]:
        """ type(config.float('wait_time')) in [float, None] """
        return self.get(item, cast=SimpleConverter(float))

    def bool(self, item: str) -> t.Optional[float]:
        """ config.bool('DEBUG') in [True, False, None] """
        # Тут используется не универсальный преобразователь
        return self.get(item, cast=BoolConverter())

    def list(self, item: str) -> t.Optional[list]:
        """ config.list('items') -> [1, 3, 4] """
        return self.get(item, cast=PythonicConverter(empty_as=[]))

    def dict(self, item: str) -> t.Optional[dict]:
        """ config.dict('logger') -> {'mode': 'WARNING'} """
        return self.get(item, cast=PythonicConverter(empty_as=dict()))

    def str(self, item: str) -> t.Optional[dict]:
        return self.get(item, cast=SimpleConverter(str))

    def __getattr__(self, item):
        """attr_name = config.attr_name"""
        return self.get(item, raise_absent=True)

    def __getitem__(self, item):
        """attr_name = config['attr_name']"""
        return self.get(item, raise_absent=True)

    def __contains__(self, item: str):
        return self.contains(item)

    def _unsafe_access_key(self, item: str) -> t.Optional[ConfigType]:
        """Возвращает значение из _data, пытаясь его найти
        по строке виде key.subkey.otherkey или без точки
        Пример: config.get('logger.mode')
        config.get('ADMIN_ID')
        Кидает KeyError, при отсутствии ключа
        """

        if super().__contains__(item):
            return super().__getitem__(item)

        # Попытка пройти по частям ключей, разделенным точками
        keys = item.split('.')
        value = self.to_dict()
        for key in keys:
            if not hasattr(value, '__getitem__'):
                raise KeyError

            if key not in value:
                raise KeyError

            value = value[key]

        return value
