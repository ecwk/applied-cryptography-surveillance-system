from models.modeller import Schema, Model
from models.modeller import getCurrentDateTime
from util.config import config

UserSchema = Schema({
  'userId': {
    'type': 'int',
    'required': True,
    'primaryKey': True,
  },
  'username': {
    'type': 'str',
    'required': True
  },
  'password': {
    'type': 'str',
    'required': True
  },
  'challengeMsg': {
    'type': 'str',
    'required': False,
    'default': ''
  },
  'dateCreated': {
    'type': 'str',
    'default': getCurrentDateTime(),
    'required': True
  },
  'pubKey': {
    'type': 'str',
    'required': False,
    'default': '',
  },

})

UserModel = Model(UserSchema, config['PATHS']['users'])