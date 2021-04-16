import configparser
import json
import re
import warnings
from abc import ABCMeta, abstractmethod
from types import ModuleType
from warnings import warn

import yaml

# Название библиотеки, используется для проверок на корректность парсинга .py файлов
LIB_NAME = 'bestconfig'


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
                data_dict = yaml.load(file, Loader=yaml.Loader)
                if not isinstance(data_dict, dict):
                    warnings.warn(f"Error parsing file: {filepath}", SyntaxWarning)
                return data_dict or {}
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
    Парсит файлы с расширениями .ini или .cfg
    Считывает файл и предоставляет словарь с ключами - секциями
    Пример:
    # config.cfg
    [bitbucket.org]
    User = hg

    [topsecret.server.com]
    Port = 50022
    ForwardX11 = no

    # main.py
    config = Config()
    config.get('topsecret.server.com').Port
    """
    extension = 'ini'

    @classmethod
    def read(cls, filepath: str) -> dict:
        parser = configparser.ConfigParser()
        # Read file with case sensitive keys
        parser.optionxform = str
        parser.read(filepath)
        sections = parser.sections()
        return {
            section_name: dict(parser[section_name])
            for section_name in sections
        }


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
        template = re.compile(r'''\s*^([^\s#=]+)\s*=\s*(?:[\s"']*)(.*?)(?:[\s"']*)$''')
        result = {}
        with open(filepath, 'r') as ins:
            for line in ins:
                match = template.match(line)
                if match is not None:
                    result[match.group(1)] = match.group(2)
        return result


class PyParser(AbstractFileParser):
    """
    ЭКСПЕРЕМЕНТАЛЬНАЯ ФИЧА
    Файл выполняется и переменные
    из него возвращаются в виде словаря ключ: значение
    Внимание: файл не должен иметь зависимостей, выполняется код
    функцией exec. Если в нем есть import, поведение не определено
    """

    extension = 'env'

    @classmethod
    def read(cls, filepath: str) -> dict:
        with open(filepath, 'r') as file:
            data = file.read()

        if LIB_NAME in data:
            raise AssertionError(
                'Нельзя индексировать .py файла, в котором уже есть Config(), используйте config.update_from_locals()'
            )

        __locals = {}
        data += '\n__locals__ = locals()'
        try:
            # Выполнение кода из файла
            exec(data, __locals, __locals)
        except:
            raise SyntaxError(
                'Ошибка выполнения файла %s, скорее всего в нем есть import-ы, которые приводят к ошибки' % filepath)

        # Оставляем только локальные переменные
        keys = __locals.keys() - {'__builtins__', '__locals__'}

        # Возвращаем все локальные переменные, кроме модулей
        return {
            key: __locals[key]
            for key in keys
            if not isinstance(__locals[key], ModuleType)
        }
