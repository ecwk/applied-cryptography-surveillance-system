from cryptography.hazmat.primitives.serialization import load_ssh_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from auth import Server as AuthServer
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
    UserModel.update(
      { 'userId': user['userId'] }, 
      { 
        'challengeMsg': generateChallenge(64),
      }
    )

    challengeMsg = user['challengeMsg'].encode('utf-8')
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
    if not user:
      res.status(404)
      res.send({ 'message': 'user not found' })
      return

    user = user[0]
    challengeAttempt = body.get
    

  @app.post('/upload')
  def upload(req, res):
    body = req.body
    mac = body.get('mac')
    username = req.body('username')

  @app.listen(ADDRESS)
  def listenCallback():
    clearConsole()
    print(f'Server listening on [ { ADDRESS[0] }:{ ADDRESS[1] } ]')


user = UserModel.find({ 'username': 'cam-001' })
