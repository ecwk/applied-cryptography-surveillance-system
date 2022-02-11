import os
import pathlib

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.servers import FTPServer

os.chdir(pathlib.Path(__file__).parent.resolve())

ANONYMOUS_DIR = os.path.join(os.getcwd(), 'data/anonymous')
ADDRESS = ('127.0.0.1', 2121)


def main():
  authorizer = DummyAuthorizer()
  authorizer.add_user('cam-001', '12345', f'data/cam-001', perm='elradfmwMT')
  authorizer.add_anonymous(ANONYMOUS_DIR, perm='elradfmwMT')

  handler = FTPHandler
  handler.authorizer = authorizer



  server = FTPServer(ADDRESS, handler)

  server.serve_forever()


main()
