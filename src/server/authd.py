from auth import Server as AuthServer
from models import UserModel
from util.tools import clearConsole, generateChallenge

ADDRESS = ('127.0.0.1', 8000)
app = AuthServer()
CHALLENGE_LENGTH = 64

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

    res.status(200)
    res.send({ 'challengeMsg': user['challengeMsg'] })

  @app.post('/upload')
  def upload(req, res):
    body = req.body
    mac = body.get('mac')
    username = req.body('username')

  @app.listen(ADDRESS)
  def listenCallback():
    clearConsole()
    print(f'Server listening on [ { ADDRESS[0] }:{ ADDRESS[1] } ]')
