import threading
import trace
import sys
import time
import datetime

import controllers.logger as logger
from views import view, mainViews
import controllers.camera as camera
from controllers.camera import getPrivKey
from util.genRsa import generatePrivateKey, savePrivateKey, savePubKey
from util.config import config
from util.tools import hiddenInput, clearConsole

CAMERA_ID = config['DEFAULT'].get('username')

def main():
  privKey = None
  sessionKey = None
  cameraOn = False

  item = 1
  while True:
    item = view(
      **mainViews['main'](
        cameraOn=cameraOn,
        privKey=privKey
      ),
      activeState = item,
      items = [
        { 'text': 'Disable Camera' if cameraOn else 'Enable Camera' },
        { 'text': 'Lock Private Key' if privKey else 'Unlock Private Key' },
        { 'text': 'Generate RSA Keys' },
        { 'text': 'View Logs' },
        { 'text': 'Clear Logs' },
        { 'text': 'Settings' }
      ]
    )

    if item == 1:
      def runCamera():
        while True:
          # Authentication handshake
          challenge = camera.getChallengeMsg(CAMERA_ID)
          decryptedChallenge = camera.decryptChallenge(challenge, privKey)
          sessionKey = camera.getSessionKey(CAMERA_ID, decryptedChallenge, privKey)

          # Start Camera: each image sent is encrypted with shared AES key
          try:
            if not sessionKey:
              raise Exception("Session key not found")

            image = camera.fetchMockData()
            if len(image) == 0:
              time.sleep(1)
              logger.log(f'[{CAMERA_ID}]_Random no motion detected_{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            else:
              filename = str(CAMERA_ID) + "_" +  datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.jpg" )

              successfulUpload = False
              while successfulUpload == False:
                if camera.uploadServer(CAMERA_ID, filename, image, sessionKey, privKey):
                  logger.log(f'[{CAMERA_ID}]_Uploaded {filename}')
                  successfulUpload = True
                else:
                  logger.log(f'[{CAMERA_ID}]_Failed to upload {filename}')
                  logger.log(f'[{CAMERA_ID}]_Retrying')
  
          except KeyboardInterrupt: exit()

      if cameraOn:
        t1.kill()
        t1.join()
        # if quit before uplaoding, session still exists and must be closed
        if sessionKey:
          camera.closeSession(CAMERA_ID, privKey, sessionKey)
        cameraOn = False
        privKey = None

      else:
        if not privKey:
          print('Unlock Private Key First')
          input('Press Enter to Continue')
          continue
        t1 = ThreadWithTrace(
          target=runCamera
        )
        t1.start()
        cameraOn = True

    elif item == 2:
      if not privKey:
        passphrase = hiddenInput("Enter the key's passphrase: ").encode('utf-8')
        privKey = getPrivKey(passphrase)
        if not privKey:
          print("Invalid passphrase")
          input('Press enter to continue...')
          continue
      else:
        privKey = None
    
    elif item == 3:
      print('This will overwrite your existing keys!')
      print('You will have to move the public key to the server')
      if input('Are you sure? (y/n): ') == 'y':
        key = generatePrivateKey()

        passphrase = input("Enter the key's passphrase: ").encode('utf-8')
        savePrivateKey(key, passphrase)
        savePubKey(key)

    elif item == 4:
      clearConsole()
      logs = logger.fetchLogs()
      print('\n\n\n#### START LOG ####')
      print(logs)
      print('#### END LOG ####')
      input('Press Enter to Continue')

    elif item == 5:
      if input('Are you sure? (y/n): ') == 'y':
        logger.clearLogFile()

    elif item == 6:
      ...

    else:
      try:
        if t1.is_alive():
          t1.kill()
          t1.join()
          if sessionKey:
            camera.closeSession(CAMERA_ID, privKey, sessionKey)
      except:
        pass
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
