import pytest
from bestconfig.main import *
import os
from pathlib import Path


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
