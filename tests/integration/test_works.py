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
