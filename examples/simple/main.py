from bestconfig import Config

if __name__ == '__main__':
    config = Config()

    # Проверяем, что переменные указаны
    config.assert_contains('VALID')

    print('BOT_ID', config.bot.id)
    print('BOT_TOKEN', config.BOT_TOKEN)
    assert isinstance(config.bot.id, int)

    # Пример обращения через точку
    print('USERNAME', config.get('admin.username'))
