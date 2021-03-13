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


def test_ini_config():
    config = Config()
    assert config.get('general.value') == 34
    with pytest.raises(KeyError):
        config.get('asdf', raise_absent=True)

    with pytest.raises(KeyError):
        a = config.asdffdsa
    assert config.bool('section_a.bool_val') is False
    assert config.float('section_a.pi_val') == 3.14
    assert 'Port' in config.get('topsecret.server.com')
    assert config.get('topsecret.server.com')['Port'] == 50022
    assert config.get('bitbucket.org')['CompressionLevel'] == 9
    with pytest.raises(KeyError):
        var = config.get('bitbucket.org').unknown


def test_py_config():
    config = Config('settings.py')
    assert config.lowercase_setting == 'value'
    assert config.int('ONLY_PYTHON_VAR') == 1233
