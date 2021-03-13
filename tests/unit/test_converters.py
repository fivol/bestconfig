import pytest

from bestconfig import Config
from bestconfig.converters import *


def test_universal_converter():
    converter = UniversalConverter()
    assert converter.cast('a') == 'a'
    assert converter.cast('123') == 123
    assert converter.cast('None') is None
    assert converter.cast('[1,2,3]') == [1, 2, 3]
    assert converter.cast('"abc"') == 'abc'
    assert converter.cast('0') == 0
    assert converter.cast('.123') == .123
    assert converter.cast('hello world') == 'hello world'
    assert converter.cast('[]') == []
    assert converter.cast('') == ''
    assert converter.cast('None') is None
    assert converter.cast('False') is False
    assert converter.cast('17321') == 17321
    assert converter.cast('bool(123)') == 'bool(123)'
    assert converter.cast('str()') == 'str()'
    assert converter.cast('-') == '-'


def test_default_get():
    config = Config()
    assert config.get('limit_users') == 10
    assert isinstance(config.get('logger'), dict)
    config.set('a', 'b')
    config.set('b', '{1,2,3}')
    config.set('c', 'True')
    assert config.get('a') == 'b'
    assert config.get('b') == {1, 2, 3}
    assert config.get('c') is True


def test_get_bool():
    config = Config()
    config.set('a', '')
    config.set('b', '123')
    config.set('c', '0')
    config.set('d', 'on')
    config.set('e', 'False')
    config.set('g', 'OFF')
    config.set('n', 'hello')
    assert config.bool('a') is False
    assert config.bool('b') is True
    assert config.bool('c') is False
    assert config.bool('d') is True
    assert config.bool('e') is False
    assert config.bool('g') is False
    assert config.bool('n') is True


def test_cast():
    config = Config()
    config.set('1', 123)
    assert config.str('1') == '123'
    config.set('a', 123)
    assert config.bool('a') is True
    config.set('a', False)
    assert config.bool('a') is False
    config.set('a', {1: 2})
    assert config.dict('a') == {1: 2}
    config.set('a', 'asdfs')
    assert config.dict('a') is None
    config.set('a', '[[[')
    assert config.list('a') is None
    config.set('a', [1, 2, 3])
    assert config.list('a') == [1, 2, 3]
    config.set('a', '')
    assert config.list('a') == []
    config.set('a', '{}')
    assert config.dict('a') == {}
    config.set('', '')

