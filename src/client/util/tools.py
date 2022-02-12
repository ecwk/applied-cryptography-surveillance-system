import re
import os
import sys
import datetime
from msvcrt import getch


def clearConsole():
  """Clears console on Linux or Windows"""
  if os.name == "nt": # windows
    os.system("cls")
  elif os.name == "posix": # mac
    os.system("clear")
  else:
    raise OSError("Your operating system is not supported.")


def hideStr(string):
  hiddenStr = ""
  for char in string:
    hiddenStr += "*"
  return hiddenStr


def hiddenInput(output=''):
  print(output, end="")
  value = []
  inputLen = 0
  while True:
    char = getch()
    decodedChar = char.decode()
    regex = '[0-9A-Za-z!@#$%^&*()]'
    match = re.match(regex, decodedChar)
    if match:
      match = match.group()
      value.append(match)
      print('*', end="")
      inputLen += 1
    else:
      pass

    if char == b'\x08':
      if not inputLen == 0:
        sys.stdout.write('\b \b')
        value.pop()
        inputLen -= 1
    elif char == b'\r':
      processedVal = ''
      for char in value:
        processedVal += char
      print('')
      return processedVal


def getDateStr():
  return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")