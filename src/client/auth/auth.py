import os
import pathlib
import random

from cryptography.hazmat.primitives.serialization import load_ssh_private_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from auth import AuthApi
from util.config import config
from util.tools import fetchMockData

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
    symmetricKey = body.get('sessionKey')
  else:
    symmetricKey = body.get('message')


  return symmetricKey



def uploadServer(filename, data, sessionKey):
  # try:
  #   if random.randrange(1,10) > 8: raise Exception("Generated Random Network Error")   # create random failed transfer   
    
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
      'username': USERNAME,
      'filename': filename,
      'data': encryptedData,
      'iv': iv
    })
    body = response['body']
    ## THIS WILL BE TRANSFERRED TO SERVER, ftp calls made on loopback addr
    # ftp = FTP()
    # ftp.connect(SERVER_IP , SERVER_PORT)

    # camId = str(CAMERA_ID).rjust(3, '0')
    # username = f'cam-{camId}'
    # password = ''
    # ftp.login(username, password)

    # ftp.storbinary('STOR ' + file_name, io.BytesIO( file_data ) )
    # ftp.quit()
    return True
  # except Exception as e:
  #   print(e, "while sending", filename )
  #   return False


# decryptor = cipher.decryptor()
# plaintext = decryptor.update(ciphertext) + decryptor.finalize()
# # remove space padding
# plaintext = plaintext.rstrip(b' ')

# print(plaintext)
