import threading

from ftpd import startFtpServer
from authd import startAuthServer

t1 = threading.Thread(target=startFtpServer)
t2 = threading.Thread(target=startAuthServer)

t1.start()
t2.start()
