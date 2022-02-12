import os
import pathlib
import time
import datetime
import base64
import random

import controllers.logger as logger
from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from auth import AuthApi
from util.config import config

os.chdir(pathlib.Path(__file__).parent.resolve())
PADDING = padding.OAEP(
  mgf=padding.MGF1(algorithm=hashes.SHA256()),
  algorithm=hashes.SHA256(),
  label=None
)

def getPrivKey(passphrase: bytes):
  privateKey = ''

  try:
    with open('../keys/id_rsa', 'r') as f:
      privateKey = f.read().encode('utf-8')
      privateKey = load_ssh_private_key(
        privateKey,
        password=passphrase
      )
  except ValueError:
    return None
  return privateKey


def getChallengeMsg(username):
  response = AuthApi.post('/challenge', {
    'username': username,
  })
  body = response['body']

  challengeMsg = None
  if response['status'] == 200:
    challengeMsg = body.get('challengeMsg')
  else:
    challengeMsg = body.get('message')

  return challengeMsg


def decryptChallenge(challengeMsg, privateKey):
  try:
    decrypted = privateKey.decrypt(
      challengeMsg,
      PADDING
    )
  except ValueError as e:
    print(e)
    print('Invalid private key')
    return None

  return decrypted


def getSessionKey(username, decryptedChallenge, privateKey):
  response = AuthApi.post('/solveChallenge', {
    'username': username,
    'challengeMsg': decryptedChallenge,
  })
  body = response['body']

  sessionKey = None
  if response['status'] == 200:
    sessionKey = body.get('sessionKey')
  else:
    sessionKey = body.get('message')

  try:
    decryptedSessionKey = privateKey.decrypt(
      sessionKey,
      padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
      )
    )
  except ValueError as e:
    print('Invalid private key')
    print(e)
    return None
  return decryptedSessionKey


def uploadServer(username, filename, data, sessionKey):
  try:
    if random.randrange(1,10) > 8: raise Exception("Generated Random Network Error")   # create random failed transfer   
    
    # initialise AES encryptor
    algorithm = algorithms.AES(sessionKey)
    iv = os.urandom(16)
    mode = modes.CBC(iv)
    cipher = Cipher(algorithm, mode)
    encryptor = cipher.encryptor()

    # encrypt data
    extra = len(data) % 16
    if extra > 0:
      data = data + (b' ' * (16 - extra))

    encryptedData = encryptor.update(data) + encryptor.finalize()

    response = AuthApi.post('/upload', {
      'username': username,
      'filename': filename,
      'data': encryptedData,
      'iv': iv
    })
    body = response['body']
    return True
  except Exception as e:
    logger.log(f'[{username}]_{e} while uploading {filename}_{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    return False


def fetchMockData() -> bytes:
  """This function simulate a motion activated camera unit.  It will return 0 byte if no motion is detected.
  Returns:
    bytes: a byte array of a photo or 0 byte no motion detected
  """    
  
  my_pict = "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"

  time.sleep(1) # simulate slow processor
  if random.randrange(1,10) > 8:  # simulate no motion detected
    return b''
  else:
    return base64.b64decode(my_pict)


def closeSession(username, privateKey):
  data = b'close'

  # sign the data
  signature = privateKey.sign(
    data,
    padding.PSS(
      mgf=padding.MGF1(hashes.SHA256()),
      salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
  )

  # encrypt data
  ...
  
  response = AuthApi.post('/close', {
    'username': username,
    'message': data,
    'signature': signature
  })
  
  return True