"""
Основной конфигурационный файл для проекта
"""

from bestconfig import Config

config = Config('dev.env')

config.assert_contains('VALID')

