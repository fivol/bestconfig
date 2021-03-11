import configparser
import json
import re
from abc import ABCMeta

import yaml


class AbstractFileParser(metaclass=ABCMeta):
    """
    Родительский класс для парсеров конфигов различных форматов
    """

    """
    Расширение файла, которое обрабатывает данный класс,
    должно переопределяться в наследниках
    """
    extension = ''

    @classmethod
    @abstractmethod
    def read(cls, filepath: str) -> dict:
        """
        :param filepath: полный путь до файла соответствующего типа (extension)
        :return: считанные из файла данные в виде python словаря
        Возбуждает FileNotFoundError при отсутствии файла
        Бросает SyntaxError если файл не соответствует формату
        """
        pass


class YamlParser(AbstractFileParser):
    """Парсит файлы с расширением .yaml"""
    extension = 'yaml'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            try:
                return yaml.load(file, Loader=yaml.Loader)
            except yaml.YAMLError:
                raise SyntaxError


class JsonParser(AbstractFileParser):
    """Парсит файлы с расширением .json"""
    extension = 'json'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                raise SyntaxError


class IniParser(AbstractFileParser):
    """Основана на configparser (https://docs.python.org/3/library/configparser.html)
    Считывает файл и предоставляет словарь с ключами - секциями"""
    extension = 'ini'

    @classmethod
    def read(cls, filepath: str) -> dict:
        # TODO протестировать
        parser = configparser.ConfigParser()
        parser.read(filepath)
        return dict(parser)


class EnvParser(AbstractFileParser):
    """Читает .env файлы и подобные ему.
    Файл должен быть в формате VAR_NAME=VAR_VALUE"""

    extension = 'env'

    @classmethod
    def read(cls, filepath: str) -> dict:
        """
        Считывает файл в формате VAR=VALUE в словарь
        Пропускает одинарные и двойные кавычки
        Пропускает комментарии
        """
        template = re.compile(r'''^([^\s#=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
        result = {}
        with open(filepath, 'r') as ins:
            for line in ins:
                match = template.match(line)
                if match is not None:
                    result[match.group(1)] = match.group(2)
        return result
