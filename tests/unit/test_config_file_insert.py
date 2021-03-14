from bestconfig import Config

config = Config()

config.insert({
    'name': 'Ivan',
    'lastname': 'Urgant'
})

FULL_NAME = f'{config.name} {config.lastname}'


def test_update_with():
    pass

