import typing as t
from warnings import warn
from bestconfig.converters import *

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
        self._data: dict = data
        self._modified: bool = False
        super().__init__(data)

    def get(self, item, default_value=None, raise_absent=False,
            cast: AbstractConverter = default_converter) -> ConfigType:
        """
        Обращается к self._data и возвращает собственный экземпляр, если значение dict
        в противном случае само значение

        attr_name = config.get('attr_name', 123)
        """
        if item in self._data:
            value = self._data[item]
            # Возвращаем словарь в виде класса ConfigProvider
            if isinstance(value, dict):
                return self.__class__(self._data[item])
            # Преобразуем объект в соответствии с переданным в параметрах cast
            if cast:
                return cast.cast(value)
            return value

        if raise_absent:
            raise KeyError

        return default_value

    def __getattr__(self, item):
        """
        attr_name = config.attr_name
        """
        return self.get(item, raise_absent=True)

    def __getitem__(self, item):
        """
        attr_name = config['attr_name']
        """
        return self.get(item, raise_absent=True)

    def __len__(self):
        return len(self.__dict__)

    def set(self, item: str, value: ConfigType):
        """Устанавливает значение по ключу"""
        if not item:
            warn('Использование пустой строки в качестве ключа', UserWarning)
        self._modified = True
        self._data[item] = value

    def to_dict(self) -> dict:
        """Возвращает весь конфигурационные словарь, содержащий имеющиеся данные
        Эквивалентно dict(config)"""
        return self._data

    def assert_contains(self, item: str):
        """Бросает исключение KeyError, если ключ не найден"""
        self.get(item, raise_absent=True)

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
