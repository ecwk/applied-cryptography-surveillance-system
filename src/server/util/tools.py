import os
import string
import random

def clearConsole():
  """Clears console on Linux or Windows"""
  if os.name == "nt": # windows
    os.system("cls")
  elif os.name == "posix": # mac
    os.system("clear")
  else:
    raise OSError("Your operating system is not supported.")

def generateChallenge(length):
  """Generates a random string of length characters"""
  return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))