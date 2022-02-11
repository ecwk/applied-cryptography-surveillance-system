import os

def clearConsole():
  """Clears console on Linux or Windows"""
  if os.name == "nt": # windows
    os.system("cls")
  elif os.name == "posix": # mac
    os.system("clear")
  else:
    raise OSError("Your operating system is not supported.")
