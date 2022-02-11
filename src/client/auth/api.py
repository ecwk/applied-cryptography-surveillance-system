import socket

HEADER_LENGTH = 64
ENCODING = 'utf-8'
SERVER_ADDRESS = ('127.0.0.1', 8000)

class Api:
  def __init__(self, options=None):
    self.address = options.get('serverAddress') or ('127.0.0.1', 8000)
  def get(self, path):
    with self.openSock() as conn:
      conn.connect(self.address)
      # Send the GET request
      req = {
        'method': 'GET',
        'path': path,
        'body': None
      }
      self.sendReq(conn, req)

      # Receive Response
      res = self.receiveRes(conn)
      # Parse Response
      try:
        res = self.parseRes(res)
      except Exception as e:
        res = {
          'status': 500,
          'body': {
            'message': 'the server has sent an invalid response',
            'error': str(e)
          }
        }
      return res

  def post(self, path, body):
    with self.openSock() as conn:
      conn.connect(self.address)
      # Send the POST request
      req = {
        'method': 'POST',
        'path': path,
        'body': body
      }
      self.sendReq(conn, req)

      # Receive Response
      res = self.receiveRes(conn)
      # Parse Response
      try:
        res = self.parseRes(res)
      except Exception as e:
        res = {
          'status': 500,
          'body': {
            'message': 'the server has sent an invalid response',
            'error': str(e)
          }
        }
      return res

  def put(self, path, body):
    with self.openSock() as conn:
      conn.connect(self.address)
      # Send the PUT request
      req = {
        'method': 'PUT',
        'path': path,
        'body': body
      }
      self.sendReq(conn, req)

      # Receive Response
      res = self.receiveRes(conn)
      # Parse Response
      try:
        res = self.parseRes(res)
      except Exception as e:
        res = {
          'status': 500,
          'body': {
            'message': 'the server has sent an invalid response',
            'error': str(e)
          }
        }
      return res

  def delete(self, path, body):
    with self.openSock() as conn:
      conn.connect(self.address)
      # Send the DELETE request
      req = {
        'method': 'DELETE',
        'path': path,
        'body': body
      }
      self.sendReq(conn, req)

      # Receive Response
      res = self.receiveRes(conn)
      # Parse Response
      try:
        res = self.parseRes(res)
      except Exception as e:
        res = {
          'status': 500,
          'body': {
            'message': 'the server has sent an invalid response',
            'error': str(e)
          }
        }
      return res

  @staticmethod
  def openSock():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  @staticmethod
  def sendReq(conn, req):
    req = str(req)
    reqLength = str(len(req)).encode(ENCODING)
    reqLength = reqLength.ljust(HEADER_LENGTH) # padding to 64 bytes
    req = req.encode(ENCODING)
    conn.send(reqLength)
    conn.send(req)

  @classmethod
  def receiveRes(cls, conn):
    resLength = conn.recv(HEADER_LENGTH)
    if not resLength:
      return None
    resLength = int(resLength.decode(ENCODING))
    res = cls.recvAll(conn, resLength)
    return res

  @staticmethod
  def recvAll(conn, length):
    data = b''
    while len(data) < length:
      packet = conn.recv(length - len(data))
      if not packet:
        return None
      data += packet
    return data

  @staticmethod
  def parseRes(res):
    res = res.decode(ENCODING)
    res = eval(res)
    return res

AuthApi = Api({
  'serverAddress': SERVER_ADDRESS
})
