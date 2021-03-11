from bestconfig import Config
import pytest


@pytest.fixture
def config():
    return Config()


def test_working():
    config = Config()


