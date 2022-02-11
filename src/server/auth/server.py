import socket
import threading

ENCODING = 'utf-8'
HEADER_LENGTH = 64

class Server:
  def __init__(self):
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.routes = []

  def get(self, path):
    def wrapper(routeMiddleware):
      self.routes.append({
        'method': 'GET',
        'path': path,
        'routeMiddleware': routeMiddleware
      })

    return wrapper

  def post(self, path):
    def wrapper(routeMiddleware):
      self.routes.append({
        'method': 'POST',
        'path': path,
        'routeMiddleware': routeMiddleware
      })

    return wrapper

  def put(self, path):
    def wrapper(routeMiddleware):
      self.routes.append({
        'method': 'PUT',
        'path': path,
        'routeMiddleware': routeMiddleware
      })

    return wrapper

  def delete(self, path):
    def wrapper(routeMiddleware):
      self.routes.append({
        'method': 'DELETE',
        'path': path,
        'routeMiddleware': routeMiddleware
      })

    return wrapper

  def listen(self, address, backlog=5):
    def wrapper(callback):
      self.socket.bind(address)
      self.socket.listen(backlog)
      callback()
      while True:
        conn, addr = self.socket.accept()
        thread = threading.Thread(target=handleRequest, args=(conn, addr))
        thread.start()

    def handleRequest(conn, addr):
      print(f'Connection from {addr}')
      with conn:
        # Receive Request
        req = receiveReq(conn)

        # Parse Request
        try:
          req = parseReq(req)
          res = Response(conn)
        except Exception as e:
          res = Response(conn)
          res.send({
            'status': 400,
            'body': {
              'message': 'the server does not understand the request',
              'error': str(e)
            }
          })
          return

        # Run Middleware
        ...
        
        # Run Routes
        self.runRoutes(req, res)

    return wrapper

  def runRoutes(self, req, res):
    method = req.method
    path = req.path
    
    # possibleRoutes = []
    for route in self.routes:
      if method == route['method'] and path == route['path']:
        # possibleRoutes.append(route)
        route['routeMiddleware'](req, res)

  

def receiveReq(conn):
  reqLen = conn.recv(HEADER_LENGTH).decode(ENCODING)
  if not reqLen:
    return None
  reqLen = int(reqLen)
  req = recvAll(conn, reqLen)
  return req

def recvAll(conn, length):
  data = b''
  while len(data) < length:
    packet = conn.recv(length - len(data)) # incase data > buffer size limit
    if not packet:
      break
    data += packet
  return data

class Request:
  def __init__(self, req):
    self.method = req['method']
    self.path = req['path']
    self.body = req['body']

def parseReq(req):
  req = req.decode(ENCODING)
  req = eval(req)
  req = Request(req)
  return req

class Response:
  def __init__(self, socket):
    self.socket = socket
    self.message = {
      'status': 200,
      'body': 'Hello World'
    }

  def status(self, status):
    self.message['status'] = status

  def send(self, body):
    self.message['body'] = body
    res = str(self.message)
    resLength = str(len(res)).encode(ENCODING)
    resLength = resLength.ljust(HEADER_LENGTH)
    res = res.encode(ENCODING)
    self.socket.send(resLength)
    self.socket.send(res)

def sendRes(conn, res):
  res = str(res)
  resLength = str(len(res)).encode(ENCODING)
  resLength = resLength.ljust(HEADER_LENGTH)
  res = res.encode(ENCODING)
  conn.send(resLength)
  conn.send(res)
