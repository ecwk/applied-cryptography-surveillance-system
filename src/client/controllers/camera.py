import time
import datetime

from auth.auth import getChallengeMsg, decryptChallenge, getSessionKey, uploadServer
from util.tools import fetchMockData
from util.config import config

CAMERA_ID = config['DEFAULT']['username']


def authenticateServer():
  challengeMsg = getChallengeMsg(CAMERA_ID)
  decrypted = decryptChallenge(challengeMsg)
  sessionKey = getSessionKey(decrypted)
  return sessionKey


def runCamera(filename, data):
  SESSION_KEY = authenticateServer()
  while True:
    try:
      if not SESSION_KEY:
        raise Exception("Session key not found")

      image = fetchMockData()
      if len(image) == 0:
        time.sleep(10)
        print("Random no motion detected")
      else:
        filename = str(CAMERA_ID) + "_" +  datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.jpg" )
      if uploadServer(filename, data, SESSION_KEY):
        print(filename, "sent")
    except KeyboardInterrupt: exit()