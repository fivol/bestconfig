"""
Основной конфигурационный файл для проекта
"""

from bestconfig import Config, Source

config = Config('dev.env', exclude=[Source.env])

config.assert_contains('VALID')

print(config)
