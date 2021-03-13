"""
Точка входа в модуль app
"""

from bestconfig import Config

config = Config()

if __name__ == '__main__':
    authorized_user_limit = config.int('limits.authorized.messages_per_second')

    DEBUG = config.bool('DEBUG')

    if DEBUG:
        print('RUN IN DEBUG MODE')
    else:
        print('RUN IN PRODUCTION MODE')
