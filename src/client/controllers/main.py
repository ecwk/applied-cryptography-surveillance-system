import threading
import trace
import sys

from views import view, mainViews
from auth import onCamera
from util.genRsa import generatePrivateKey, savePrivateKey, savePubKey
from util.config import config

USERNAME = config['DEFAULT'].get('username')

def main():
  cameraOn = False

  item = 1
  while True:
    item = view(
      **mainViews['main'](
        cameraOn=cameraOn
      ),
      activeState = item,
      items = [
        { 'text': 'Disable Camera' if cameraOn else 'Enable Camera' },
        { 'text': 'Generate RSA Keys' },
        { 'text': 'Settings' }
      ]
    )

    if item == 1:
      if cameraOn:
        t1.kill()
        t1.join()
        cameraOn = False

      else:
        t1 = ThreadWithTrace(target=onCamera)
        t1.start()
        cameraOn = True
    
    elif item == 2:
      print('This will overwrite your existing keys!')
      print('You will have to move the public key to the server')
      if input('Are you sure? (y/n): ') == 'y':
        key = generatePrivateKey()
        savePrivateKey(key)
        savePubKey(key)

    elif item == 3:
      ...

    else:
      if t1.is_alive():
        t1.kill()
        t1.join()
      exit()



class ThreadWithTrace(threading.Thread):
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
 
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run     
    threading.Thread.start(self)
 
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
 
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
 
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
 
  def kill(self):
    self.killed = True
