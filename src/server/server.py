# need to pip install pytftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer() # handle permission and user
authorizer.add_anonymous("./data/" , perm='adfmwM')
handler = FTPHandler #  understand FTP protocol
handler.authorizer = authorizer
server = FTPServer(("127.0.0.1", 2121), handler) # bind to high port, port 21 need root permission
server.serve_forever()


