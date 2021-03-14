from bestconfig import Config

config = Config()

config.insert({
    'name': 'Ivan',
    'lastname': 'Urgant'
})

FULL_NAME = f'{config.name} {config.lastname}'

config.update_from_locals()


def test_update_from_locals():
    assert config.get('FULL_NAME') == 'Ivan Urgant'


def test_update_from_func():
    config = Config(exclude_default=True)
    assert len(config) == 0
    ONLY_VAR = 123
    config.update_from_locals()
    print(config)
    assert len(config) == 1
