import pytest
import os

from bestconfig.adapters import *
from bestconfig.source import Source


def test_env_adapter():
    source = Source(Source.env)
    os.environ['var1'] = 'val1'
    os.environ['var2'] = '2'

    data = EnvAdapter().get_dict(source)
    assert data['var1'] == 'val1'

    assert data['var2'] == '2'
