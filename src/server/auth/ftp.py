import os
import pathlib
from ftplib import FTP
import io

from util.config import config

os.chdir(pathlib.Path(__file__).parent.resolve())
SERVER_IP = "127.0.0.1"
SERVER_PORT = 2121
USERNAME = config['DEFAULT'].get('username')


def uploadToFtpd(username, filename, data):
  ftp = FTP()
  ftp.connect(SERVER_IP , SERVER_PORT)

  ftp.login(username, '')
  ftp.storbinary('STOR ' + filename, io.BytesIO( data ) )
  ftp.quit()
  return True
