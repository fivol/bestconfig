import os

from bestconfig import Config
from tests.integration.project.subfolder.module import get_path

if __name__ == '__main__':
    config = Config()
    config.assert_contains('VERSION')
    print(os.path.abspath(__file__), get_path(), os.getcwd())


