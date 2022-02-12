import os
import datetime

from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from auth import Server as AuthServer
from auth.ftp import uploadToFtpd
from models import UserModel
from util.tools import clearConsole, generateChallenge

ADDRESS = ('127.0.0.1', 8000)
app = AuthServer()
CHALLENGE_LENGTH = 64
PADDING = padding.OAEP(
  mgf=padding.MGF1(algorithm=hashes.SHA256()),
  algorithm=hashes.SHA256(),
  label=None
)

# In-memory Session Storage
USER_SESSIONS = [
  # {
  #   'userId': 1,
  #   'challengeMsg': generateChallenge(64),
  #   'sessionKey': os.urandom(16)
  # }
]
def getSession(userId):
  for session in USER_SESSIONS:
    if session['userId'] == userId:
      return session
  return None


def startAuthServer():
  @app.post('/challenge')
  def getChallenge(req, res):
    body = req.body
    username = body.get('username')
    user = UserModel.find({ 'username': username })
    if not user:
      res.status(404)
      res.send({ 'message': 'user not found' })
      return

    user = user[0]
    session = None
    for i, _user in enumerate(USER_SESSIONS):
      if _user['userId'] == user['userId']:
        USER_SESSIONS[i]['challengeMsg'] = generateChallenge(CHALLENGE_LENGTH)
        session = USER_SESSIONS[i]
        break
    if session is None:
      session = {
        'userId': user['userId'],
        'challengeMsg': generateChallenge(CHALLENGE_LENGTH),
        'sessionKey': None
      }
      USER_SESSIONS.append(session)

    challengeMsg = session['challengeMsg'].encode('utf-8')
    pubKey = user['pubKey'].encode('utf-8')
    pubKey = load_ssh_public_key(pubKey)
    encryptedChallenge = pubKey.encrypt(
      challengeMsg,
      PADDING
    )
 
    res.status(200)
    res.send({ 'challengeMsg': encryptedChallenge })


  @app.post('/solveChallenge')
  def solveChallenge(req, res):
    body = req.body
    username = body.get('username')
    user = UserModel.find({ 'username': username })

    # Request Validifications
    if not user:
      res.status(404)
      res.send({ 'message': 'user not found' })
      return
    user = user[0]
    session = getSession(user['userId'])
    if session is None:
      res.status(404)
      res.send({ 'message': 'post /challenge first' })
      return

    # Solve Challenge
    challengeAttempt = body.get('challengeMsg')
    challengeMsg = session['challengeMsg'].encode('utf-8')

    # If correct, remove current challengeMsg from memory
    if challengeAttempt == challengeMsg:

      # if session already exists
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          session['challengeMsg'] = None
          sessionKey = os.urandom(16)
          USER_SESSIONS[i]['sessionKey'] = sessionKey
          break

      # Encrypt sessionKey with pubKey before sending
      pubKey = user['pubKey'].encode('utf-8')
      pubKey = load_ssh_public_key(pubKey)
      encryptedSessionKey = pubKey.encrypt(
        sessionKey,
        PADDING
      )

      res.status(200)
      res.send({ 'sessionKey': encryptedSessionKey })
      print(USER_SESSIONS)
    else:
      res.status(401)
      res.send({ 'message': 'incorrect challenge attempt' })


  @app.post('/upload')
  def upload(req, res):
    body = req.body
    username = body.get('username')
    filename = body.get('filename')
    data = body.get('data')
    iv = body.get('iv')

    # Request Validifications
    if not (username and filename and data and iv):
      res.status(404)
      res.send({ 'message': 'missing parameters' })
      return
    user = UserModel.find({ 'username': username })
    if not user:
      res.status(404)
      res.send({ 'message': 'user not found' })
      return
    user = user[0]

    # check if sessionKey exists
    sessionKey = None
    for user_ in USER_SESSIONS:
      if user_['userId'] == user['userId']:
        sessionKey = user_['sessionKey']
        break
      if sessionKey is None:
        res.status(400)
        res.send({ 'message': 'post /solveChallenge first' })
        return

    try:
      # initialise AES decryptor
      algorithm = algorithms.AES(sessionKey)
      mode = modes.CBC(iv)
      cipher = Cipher(algorithm, mode)
      decryptor = cipher.decryptor()

      # decrypt data
      decryptedData = decryptor.update(data) + decryptor.finalize()
      decryptedData = decryptedData.rstrip(b' ')

      # if data is to close connection/session
      if decryptedData == b'close':
        for i, session in enumerate(USER_SESSIONS):
          if session['userId'] == user['userId']:
            del USER_SESSIONS[i]
            break
      else:
      # upload file via ftp on server's loopback
        print(f'sent {filename}')
        uploadToFtpd(username, filename, decryptedData)
      
      # remove current session key from memory
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          USER_SESSIONS[i]['sessionKey'] = None
          break

    except Exception as e:
      # if wrong sessionKey
      print(e)
      res.status(400)
      res.send({ 'message': f'{e}' })
      return

    res.status(200)
    res.send({ 'message': 'uploaded' })


  @app.listen(ADDRESS)
  def listenCallback():
    clearConsole()
    print(f'Server listening on [ { ADDRESS[0] }:{ ADDRESS[1] } ]')
