## Тут описан проект в качестве python библиотеки

[Статья по созданию пакета](https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f)

[Статья по публикации](https://realpython.com/pypi-publish-python-package/)

Запустить тесты из папки `tests`
```
python setup.py pytest
```
Собрать библиотеку в папку `dist`
```
python setup.py bdist_wheel
или 
python setup.py sdist bdist_wheel
```