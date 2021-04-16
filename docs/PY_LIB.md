## Тут описан проект в качестве python библиотеки

[Статья по созданию пакета](https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f)

[Статья по публикации](https://realpython.com/pypi-publish-python-package/)

Для сборки понадобится
```shell
pip install twine
```

Запустить тесты из папки `tests`
```
python setup.py pytest
```
Собрать библиотеку в папку `dist`. Не забываем увеличить версию в файле [setup.py](setup.py)
```
python setup.py sdist bdist_wheel
```
Проверить корректность конфигурации
```shell
twine check dist/*
```
Загрузить на [test.pypi.org](https://test.pypi.org)
```shell
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```
Загрузить на [pypi.org](https://pypi.org)
```shell
twine upload dist/*
```

Локально запустить `pip install`, **внимание, нужно указать нужную версию
вместо 1.0.1**
```shell
pip install dist/bestconfig-1.0.1-py3-none-any.whl
```