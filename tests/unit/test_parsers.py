import pytest
import os
from pathlib import Path

from bestconfig.file_parsers import YamlParser, EnvParser, IniParser


@pytest.fixture
def curr_dir():
    return os.path.dirname(__file__)


def test_env_parser(curr_dir):
    assert Path(curr_dir).exists()
    filepath = Path(os.path.join(curr_dir, '.env'))
    assert filepath.exists()
    d = EnvParser.read(filepath)
    assert d.get('VAR') == 'VALUE'
    assert d.get('ANOTHER') == '10'
    assert d.get('QUOTES') == '11'
    assert d.get('DEBUG') == 'true'
    assert '#' not in d


def test_empty_env(curr_dir):
    filepath = Path(os.path.join(curr_dir, 'empty.env'))
    assert 0 == len(EnvParser.read(filepath))
    assert isinstance(EnvParser.read(filepath), dict)


def test_yaml_broken(curr_dir):
    filepath = Path(os.path.join(curr_dir, 'broken.yaml'))
    # with open(filepath, 'r') as f:
    #     print(yaml.unsafe_load(f))
    with pytest.raises(SyntaxError):
        YamlParser.read(filepath)


def test_yaml_parser(curr_dir):
    filepath = Path(os.path.join(curr_dir, 'config.yaml'))
    d = YamlParser.read(filepath)
    assert isinstance(d, dict)
    assert 'logger' in d
    assert 'mode' in d['logger']
    assert d['logger']['mode'] == 'DEBUG'


def test_cfg_parser(curr_dir):
    filepath = Path(os.path.join(curr_dir, 'config.cfg'))
    data = IniParser.read(filepath)
    assert 'topsecret.server.com' in data
    assert data['bitbucket.org']['User'] == 'hg'


def test_ini_parser(curr_dir):
    filepath = Path(os.path.join(curr_dir, 'config.ini'))
    data = IniParser.read(filepath)
    assert 'section_a' in data
    assert data['section_a']['string_val'] == 'hello'
    assert data['section_a']['bool_val'] == 'false'
    assert data['general']['value'] == '34'




