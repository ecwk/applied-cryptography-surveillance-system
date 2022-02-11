import os
import pathlib

from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from auth import AuthApi
from util.config import config

os.chdir(pathlib.Path(__file__).parent.resolve())
USERNAME = config['DEFAULT'].get('username')

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


def decryptChallenge(challengeMsg):
  privateKey = ''
  with open('../keys/id_rsa', 'r') as f:
    privateKey = f.read().encode('utf-8')
    privateKey = load_ssh_private_key(privateKey, password=None)

    try:
      decrypted = privateKey.decrypt(
        challengeMsg,
        padding.OAEP(
          mgf=padding.MGF1(algorithm=hashes.SHA256()),
          algorithm=hashes.SHA256(),
          label=None
        )
      )
    except ValueError:
      print('Invalid private key')
      return None

  return decrypted


def getSessionKey(decryptedChallenge):
  response = AuthApi.post('/solveChallenge', {
    'username': USERNAME,
    'challengeMsg': decryptedChallenge,
  })
  body = response['body']

  symmetricKey = None
  if response['status'] == 200:
    symmetricKey = body.get('symmetricKey')
  else:
    symmetricKey = body.get('message')


  return symmetricKey