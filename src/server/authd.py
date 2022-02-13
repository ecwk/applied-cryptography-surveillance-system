import os
import datetime
from pprint import pprint

from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.exceptions import InvalidSignature

from auth import Server as AuthServer
from auth.ftp import uploadToFtpd
from models import UserModel
from util.tools import clearConsole

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
  # {  for example
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

    # Request Validations
    if not user:
      res.status(404)
      res.send({ 'message': 'user not found' })
      return
    user = user[0]

    # Regenerate challenge if session exists
    session = None
    for i, _user in enumerate(USER_SESSIONS):
      if _user['userId'] == user['userId']:
        USER_SESSIONS[i]['challengeMsg'] = os.urandom(CHALLENGE_LENGTH)
        session = USER_SESSIONS[i]
        break

    # Generate Session if not exists
    if session is None:
      session = {
        'userId': user['userId'],
        'challengeMsg': os.urandom(CHALLENGE_LENGTH),
        'sessionKey': None
      }
      USER_SESSIONS.append(session)

    # Send encrypted challenge
    challengeMsg = session['challengeMsg']
    pubKey = user['pubKey'].encode('utf-8') # from users.csv
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
    signature = body.get('challengeMsg')

    # Request Validations
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

    # Verify Challenge Signature
    challengeMsg = session['challengeMsg']
    pubKey = user['pubKey'].encode('utf-8')
    pubKey = load_ssh_public_key(pubKey)
    try:
      pubKey.verify(
        signature,
        challengeMsg,
        padding.PSS(
          mgf=padding.MGF1(hashes.SHA256()),
          salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
      )
    except InvalidSignature:
      for i, _user in enumerate(USER_SESSIONS):
        if _user['userId'] == user['userId']:
          USER_SESSIONS.pop(i)
          break
      res.status(401)
      res.send({ 'message': 'challenge not solved' })
      return

    # if valid challenge signature, generate session key
    for i, _user in enumerate(USER_SESSIONS):
      if _user['userId'] == user['userId']:
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


  @app.post('/upload')
  def upload(req, res):
    body = req.body
    username = body.get('username')
    filename = body.get('filename')
    data = body.get('data')
    iv = body.get('iv')

    # Request Validations
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

    # check if user sessionKey exists
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

      # decrypt data
      decryptor1 = cipher.decryptor()
      decryptedData = decryptor1.update(data) + decryptor1.finalize()
      decryptedData = decryptedData.rstrip(b' ')

      # decrypt signature
      decryptor2 = cipher.decryptor()
      decryptedSignature = decryptor2.update(body.get('signature')) + decryptor2.finalize()
      decryptedSignature = decryptedSignature.rstrip(b' ')

      # verify signature
      pubKey = user['pubKey'].encode('utf-8')
      pubKey = load_ssh_public_key(pubKey)
      pubKey.verify(
        decryptedSignature,
        decryptedData,
        padding.PSS(
          mgf=padding.MGF1(hashes.SHA256()),
          salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
      )

      # upload file via ftp on server's loopback
      uploadToFtpd(username, filename, decryptedData)
      
      # remove current session
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          USER_SESSIONS.pop(i)
          break

    except InvalidSignature as e:
      res.status(401)
      res.send({ 'message': 'invalid signature' })
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          USER_SESSIONS.pop(i)
          break
      return

    except Exception as e:
      # if wrong sessionKey
      res.status(400)
      res.send({ 'message': f'{e}' })

      # remove current session
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          USER_SESSIONS.pop(i)
          break
      return
    res.status(200)
    res.send({ 'message': 'uploaded' })


  @app.post('/close')
  def close(req, res):
    body = req.body
    message = body.get('message')
    signature = body.get('signature')
    username = body.get('username')
    iv = body.get('iv')

    # Request Validations
    if not (message and signature and username and iv):
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
        print('no Key')
        input()

    # initialise AES decryptor
    algorithm = algorithms.AES(sessionKey)
    mode = modes.CBC(iv)
    cipher = Cipher(algorithm, mode)

    # decrypt message
    decryptor1 = cipher.decryptor()
    decryptedData = decryptor1.update(message) + decryptor1.finalize()
    decryptedData = decryptedData.rstrip(b' ')

    # decrypt signature
    decryptor2 = cipher.decryptor()
    decryptedSignature = decryptor2.update(body.get('signature')) + decryptor2.finalize()
    decryptedSignature = decryptedSignature.rstrip(b' ')

    try:
      # verify signature
      pubKey = user['pubKey'].encode('utf-8')
      pubKey = load_ssh_public_key(pubKey)
      pubKey.verify(
        decryptedSignature,
        decryptedData,
        padding.PSS(
          mgf=padding.MGF1(hashes.SHA256()),
          salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
      )

      # Close session if valid signature and session exists
      for i, session in enumerate(USER_SESSIONS):
        if session['userId'] == user['userId']:
          USER_SESSIONS.pop(i)
          break
    except InvalidSignature as e:
      res.status(401)
      res.send({ 'message': 'invalid signature' })
      return
      

  @app.listen(ADDRESS)
  def listenCallback():
    clearConsole()
    print(f'Server listening on [ { ADDRESS[0] }:{ ADDRESS[1] } ]')
