import os
import pathlib
import configparser

os.chdir(pathlib.Path(__file__).parent.parent.resolve())
config = configparser.ConfigParser()
config.read('config.ini')