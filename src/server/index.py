from flask import Flask

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def getUsers():
  return '<p>Hello World</p>'

if __name__ == '__main__':
  app.run(debug=True)
  