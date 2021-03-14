## Как запустить тесты
1. Склонировать репозиторий локально
```python
git clone https://github.com/fivol/bestconfig
```
2. Перейти в папку с библиотекой
```shell
cd bestconfig
```
3. Активировать виртуальное окружение
```shell
virtualenv venv &&
source venv/bin/activate
```
4. Установить зависимости
```shell
pip install -r requirements.txt
```
5. Добавляем библиотек в путь для поиска `pytest`
```shell
export PYTHONPATH=$PYTHONPATH:$PWD
```   
5. Запустить тесты
```shell
pytest tests/
```
