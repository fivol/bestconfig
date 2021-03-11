import typing as t

"""Тип, которым может быть значение конфига"""
ConfigType = t.Union[str, int, float, bool, dict, list]


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
            return self.__new__(self.__class__, self._data[item])

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

    def set(self, item: str, value: ConfigType):
        """Устанавливает значение по ключу"""
        self._modified = True
        self._data[item] = value

    def to_dict(self):
        return self._data

    def __len__(self):
        return len(self.__dict__)

    @classmethod
    def _create_object(cls, data: dict):
        obj = dict.__new__(cls)
        obj.__init__(data)
        return obj

    # TODO добавить cast к различным типам
