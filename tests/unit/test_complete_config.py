import os

import pytest

from bestconfig import Config, Source
from bestconfig.source_resolver import SourceResolver


def test_exclude():
    config = Config(exclude_default=True)
    assert len(config) == 0

    os.environ['name13'] = 'vvv'
    config = Config(exclude=[Source.env])
    assert 'name13' not in config


def test_add():
    config = Config(exclude=[Source.env])
    config.insert({
        'kkk': 'vvv'
    })
    assert config.get('kkk') == 'vvv'
    config.insert('custom.py')
    assert config.contains('INSERT_VARIABLE')
    assert config.get_raw('INSERT_VARIABLE') == '1' * 10


def test_resolver():
    import os
    resolver = SourceResolver(os.getcwd())
    assert resolver.resolve({1: 2}) == {1: 2}
