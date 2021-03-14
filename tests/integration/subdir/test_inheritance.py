import pytest

"""
Внимание, тесты нужно запускать из корневой папки test
Если запускать их по отдельности, проходить не обязаны
так как тут важна родительская директория
"""

from bestconfig import Config


def test_overload():
    config = Config()
    assert config['overload'] == 'hello'

    config = Config('config.py')
    assert config.overload == 'hello2'


def test_exclude():
    config = Config(exclude=['config.json'])
    assert config.get('overload') is None

