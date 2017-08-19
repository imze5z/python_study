from setuptools import setup, find_packages
import os

os.system('pip install -r requirements.txt')

scripts = [
    "excellib.py", "html_parserlib.py", "mongolib.py", "mysqllib.py",
    "rabbitmqlib.py", "randomlib.py", "timelib.py", "yamllib.py"
]

scripts = [os.path.sep.join(['imze5z', script]) for script in scripts]

setup(
    name="imze5z",
    version="0.10",
    description="some useful module",
    author="imze5z",
    url="http://github.com/imze5z/python_study",
    license="LGPL",
    packages=find_packages(),
    scripts=scripts)
