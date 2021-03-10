# bestconfig
### *Python модуль для работы с файлами конфигурации проекта*

## Installation
```
pip install bestconfig
```

## A Simple Example
Предположим у вас такая структура проекта
```
root/
    main.py
    config.yaml
    .env
```
`/main.py`
```python
from bestconfig import Config

config = Config("myconfig.json")
print(dict(config))
```
Содержимое файлов:

`.env`
```editorconfig
DATABASE_PASSWOD=postgres
```
`/config.yaml`
```yaml
HOST: http://localhost
PORT: 5050
logger:
  mode: WARNING
```
`myconfig.json`
```editorconfig
{
    "VERSION": "1.23.4",
    "BUILD": 5563
}
```
Вывод будет следующим
```editorconfig
{
    "logger": {
        "mode": "DEBUG"       
     }
    "PORT": 5050,
    "HOST": "http://localhost",
    "DATABASE_PASSWOD": "postgres"
}
```
## Что произошло?
1. Класс `Config` просканировал текущую дирикторию, вплоть до корня проекта
2. Нашел все указанные в аргументах файлы и те, что в списке по умолчанию 
   (например `.env`, `env_file`, `config.yaml`, `configuration.ini` и тд)
   

## Какие источники конфигов поддерживаются?
- Файлы следующих типов:
  - `.json`
  - `.yaml`
  - `.ini`
  - `.py` (если в нем нет инициализации `Config()` во избежании рекурсии)
  - `.cfg`
- Файлы в формате `CONFIG_NAME=CONFIG_VALUE`
- Уже существующие и новые переменные окружения
- Обычные `python` словари


### Файлы для поиска по умолчанию
- Все комбинации имени
  
  `config` `configuration` `settings` `conf`
  
  и расширений
  
  `.json` `.yaml` `.ini` `.env` `.cfg`
- Выеденные, часто используемые названия
    - `env_file`
    - `.env`
    - `config.py`

## Запланированные обновления
- Поддержка загрузки из базы данных
- Поддержка загрузки с config сервера


