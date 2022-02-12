import os
import pathlib

from util.config import config

os.chdir(pathlib.Path(__file__).parent.resolve())

LOG_PATH = f'../{config["PATHS"].get("log")}'

def fetchLogs(logPath = LOG_PATH):
  with open(logPath, 'r') as f:
    logs = f.read()
  return logs

def log(log, logPath = LOG_PATH):
  with open(logPath, 'a') as f:
    f.write(log + '\n')
    

def clearLogFile(logPath = LOG_PATH):
  with open(logPath, 'w') as f:
    f.write('')