import os

from bestconfig import Config
import pytest

from bestconfig.config_provider import ConfigProvider



@pytest.fixture
def config():
    return Config()


def test_working():
    config = Config()


def test_contains_configs(config):
    assert isinstance(config, dict)
    assert isinstance(config, ConfigProvider)
    assert len(config) > 0
    assert config['VARNAME'] == 'VARVALUE'
    assert config.VARNAME == 'VARVALUE'
    assert config.get('VARNAME') == 'VARVALUE'


def test_all_sources_config(config):
    assert config.AA == '_12'
    assert config.get('ENV_NAME') == 'ENV_VALUE'
    assert isinstance(config.messages_limit, int)
    assert isinstance(config.logger, ConfigProvider)
    assert config.logger.format.endswith('s')
    assert config.data.a == 4
    assert config.MY_COOL_CONFIG_VARIABLE == 228


def test_absent(config):
    with pytest.raises(KeyError):
        data = config['asdfdsf']

    assert config.get('abccccc') is None
