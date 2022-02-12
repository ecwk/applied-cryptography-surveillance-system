import os
import pathlib

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

os.chdir(pathlib.Path(__file__).parent.resolve())
PADDING = padding.OAEP(
  mgf=padding.MGF1(algorithm=hashes.SHA256()),
  algorithm=hashes.SHA256(),
  label=None
)


def generatePrivateKey():
  return rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
  )


def privateKeyBytes(key, passphrase):
  return key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.OpenSSH,
    encryption_algorithm=serialization.BestAvailableEncryption(passphrase)
  )


def publicKeyBytes(key):
  return key.public_key().public_bytes(
    encoding=serialization.Encoding.OpenSSH,
    format=serialization.PublicFormat.OpenSSH
  )


def savePrivateKey(key, passphrase):
  with open('../keys/id_rsa', 'wb') as f:
    f.write(privateKeyBytes(key, passphrase))


def savePubKey(key):
  with open('../keys/id_rsa.pub', 'wb') as f:
    f.write(publicKeyBytes(key))
