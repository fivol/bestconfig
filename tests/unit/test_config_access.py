import pytest

from bestconfig import Config


def test_dotted_access():
    config = Config()
    config.set('a', {'b': 3})
    assert config.get('a') == {'b': 3}
    assert config.get('a.b') == 3

    config.set('value', {'key': {'other': 123}})
    assert config.int('value.key.other') == 123


def test_config_in_files():
    config = Config()
    assert config.list_config == ['first', 'second', 'third']
    assert config.dict('dict_config') == {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }
    assert config.str('dict_config.key1') == 'value1'
    with pytest.raises(KeyError):
        a = config['unknown']

    assert config.get('bool_prop') is True
    assert config.bool('bool_prop') is True
    assert config.bool('false_prop') is False
    assert config.str('logger.mode') == 'DEBUG'
