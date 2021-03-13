from abc import ABCMeta, abstractmethod
import typing as t
import ast


class AbstractConverter(metaclass=ABCMeta):
    """
    Наследники данного класса являются преобразователями
    типов данных.
    Например BoolConverter.cast('true') == True
    """

    @abstractmethod
    def cast(self, value: t.Any, safe=True):
        """Принимает переменную любого типа
        Пытается сделать преобразование к определенному типу
        Если safe == False, то при ошибки бросается исключение
        Если safe == True, то при невозможности выполнить
        преобразование, None
        """
        pass


class SimpleConverter(AbstractConverter):
    """Самый простой преобразователь.
    Пытается закастовать к переданному в конструкторе типу
    Пример:
    SimpleConverter(target_type).cast(value) -> target_type(value)
    SimpleConverter(int).cast('123') == 123
    None при неудаче
    """

    def __init__(self, convert_type: type):
        self._target_type = convert_type

    def cast(self, value: t.Any, safe=True):
        if isinstance(value, self._target_type):
            return value

        try:
            return self._target_type(value)
        except (ValueError, TypeError):
            if not safe:
                raise
            return None


class PythonicConverter(AbstractConverter):
    """Конвертирует, исходя из питоновского синтекса.
    Например PythonicConverter("['hi', 234]") = ['hi', 234]
    """

    def __init__(self, empty_as=None):
        """
        :param empty_as: возвращается, если value пустая строка
        """
        self._empty_as = empty_as

    def cast(self, value: t.Any, safe=True):
        if value == '' and self._empty_as is not None:
            return self._empty_as
        if not isinstance(value, str):
            return value
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            if not safe:
                raise
            return None


class UniversalConverter(AbstractConverter):
    """
    Универсальный преобразователь
    1. Если тип значения изначально не строковый, оно возвращается as-is
    2. Производится попытка интерпретировать строку как выражение на python и вернуть его
    3. Возвращается сама строка
    """

    def cast(self, value: t.Any, safe=True):
        if not isinstance(value, str):
            return value
        try:
            return PythonicConverter().cast(value, safe=False)
        except:
            if not safe:
                raise
            return value


class BoolConverter(AbstractConverter):
    """
    'yes' -> True
    'false' -> False
    '0' -> False
    """

    def cast(self, value: t.Any, safe=True) -> bool:
        if isinstance(value, str):
            value = value.lower().strip()
            return self._mapping_dict.get(value, bool(value))

        return bool(value)

    _mapping_dict = {
        'yes': True,
        'no': True,
        'true': True,
        'false': False,
        '1': True,
        '0': False,
        'on': True,
        'off': False
    }
