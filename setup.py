import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name='bestconfig',
    packages=find_packages(include=['bestconfig']),
    version='1.0.0',
    description="""Setup your project config easily""",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/fivol/bestconfig",
    author='Boris Bondarenko',
    author_email="borisoffficial@gmail.com",
    license='MIT',
    install_requires=[
        'PyYAML==5.4.1',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==6.2.2'],
    test_suite='tests',
)
