# bestconfig
### *Python модуль для работы с файлами конфигурации проекта*

Этот модуль поможет сильно упростить использование конфигурационных
файлов, вы предпочитаете хранить константы и 
настройки в `.yaml`, `.json` или в переменных окружения?, 
Это не важно, `bestconfig` учитывает множество вариантов
и предоставляет очень удобный интерфейс доступа к данным
## Installation
```
pip install bestconfig
```

## A Simple Example
Предположим, у вас такая структура проекта
```
root/
    app:
      main.py
      myconfig.json
    config.yaml
    .env
```
`app/main.py`
```python
from bestconfig import Config

config = Config("myconfig.json")
# На этом вся настройка закончилась
# В аргументах можно передать имена файлов,
# в которых у вас хранятся настройки, если они нестандартные

# Следующие варианты эквивалентны
logger = config.get('logger')
logger = config.logger
logger = config['logger']

mode = config.logger.mode
mode = config.get('logger.mode') # -> DEBUG или None
mode = config['__unknown__'] # raise KeyError
mode = config.get('__unknown__') # return None
```
Содержимое файлов:

`.env`
```dotenv
DATABASE_PASSWOD=postgres
```
`config.yaml`
```yaml
HOST: http://localhost
PORT: 5050
logger:
  mode: WARNING
```
`myconfig.json`
```json
{
    "VERSION": "1.23.4",
    "BUILD": 5563
}
```
`config.to_dict()` покажет следующее:
```json
{
    "logger": {
        "mode": "DEBUG"       
     },
    "VERSION": "1.23.4",
    "BUILD": 5563,                     
    "PORT": 5050,
    "HOST": "http://localhost",
    "DATABASE_PASSWOD": "postgres"
}
```
## Что произошло?
1. Класс `Config` просканировал текущую директорию, вплоть до корня проекта
2. Нашел все указанные в аргументах файлы и те, что в списке по умолчанию 
   (например `.env`, `env_file`, `config.yaml`, `configuration.ini` и тд)
   

## Какие источники конфигов поддерживаются?
- Файлы следующих типов:
  - `.json`
  - `.yaml`
  - `.ini`
  - `.py` (если в нем нет инициализации `Config()` во избежание рекурсии)
  - `.cfg`
- Файлы в формате `CONFIG_NAME=CONFIG_VALUE`
- Уже существующие и новые переменные окружения
- Обычные `python` словари


### Файлы для поиска по умолчанию
- Все комбинации имени
  
  `config` `configuration` `settings` `setting` `conf`
  
  и расширения
  
  `.json` `.yaml` `.ini` `.env` `.cfg`
- Выделенные, часто используемые названия
    - `env_file`
    - `.env`
    - `config.py`
  
## Доступ к данным
1. Через точку `config.name`
1. Нотация `python dict` `config['name']`
Бросает исключение при отсутствии
1. `config.get('name', 'default_value', raise_absent=False)`   
1. `config.get('name.subname')` если параметр это тоже словарь, 
к вложенным значениям можно обращаться единым запросом через `get`, 
   вложенность не ограничена
1. Можно сразу при запросе приводить результат к определенному типу
    ```python
    config = Config()
    
    LIMIT = config.int('LIMIT')
    RATE = config.float('RATE')
    LOGGER = config.dict('logger')
    USERNAME = config.str('ADMIN_USERNAME')
    PRICES = config.list('PRICES')
    ```
    Эти функции, вернут вам значение соответствующего типа, либо,
    если преобразование не удалось - `None`
1. По умолчанию, при обращении без указания типа, происходит следующее
    1. Каждый формат файлов, например `.yaml` уже парсится с учетом типов,
  так `varname: 123` будет считано как число 123  
    1.  Если значение все равно представляет собой строку, 
  совершается попытка интерпретировать его `python` выражение, 
        так `.env` файл, содержащий `LIST=[1, 2]` станет
        ```python
        l = config.get('LIST')
        isinstance(l, list) # True
        print(l) # [1, 2]
        ```
        Чтобы избежать такого поведения, используйте
        ```python
         config.get_raw('key') 
        ```
        Возвращенное значение не будет обработано, на самом деле, эта функция всего лишь делает
    `config.get(cast=None)`. За подробностями в исходники ;)

Сохранить новую переменную, можно с помощью `set`
```python
config.set('pages_limit', 12)
print(config.get('pages_limit')) -> 12

config.set('d', {'a': 'value'})
# config.d.a == 'value'
```

Чтобы проверить, что нужные переменные окружения или файлы 
импортировались, используйте `config.assert_contains()`
```python
config.set('key', 'value')
config.assert_contains('key') # pass
config.assert_contains('key1') # raise KeyError
```
Бывает необходимо некоторым образом преобразовать 
конфиги после импорта из файлов, тогда пригодится
```python
from bestconfig import Config

config = Config()

FULL_NAME = f'{config.name} {config.lastname}'

config.update_from_locals()
```
`locals()` то есть локальные при вызове этой функции станут доступны
`config.get('FULL_NAME')`

Также иногда бывает удобно, вместо `config.set('key', 'value')`
добавить целый словарь или даже файл во время исполнения
```python
from bestconfig import Config
config = Config(exclude_default=True)

config.insert({
    'name': 'Ivan'
})
config.assert_contains('name')

# Добавить к существующим еще и `other_file.yaml`
config.insert('other_file.yaml')
```

### Можете также посмотреть

- [github](https://github.com/fivol/bestconfig)
  Остальные ссылки доступны только с оттуда (не с [pypi.org](https://pypi.org/project/bestconfig/))
- [Примеры использования](examples)
- [Как запустить тесты](docs/TESTS.md)

**Если после документации остались вопросы, 
код подробно документирован, можно смело смотреть в исходники и читать docstring**

## Запланированные обновления
- Поддержка загрузки из базы данных
- Поддержка загрузки с config сервера
- Перевод документации и комментариев на английский


