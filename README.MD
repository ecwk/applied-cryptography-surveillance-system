# ACG CA2

## Prerequisites
1) Install Python 3.9 or later
2) Install required package(s) using the command `pip install -r requirements.txt`

## To Run
### Client
1) Open another new terminal window and change directory into src/client
2) Run the command `python -m client/index.py` to start the client.

### Server
1) Open a new terminal window and change directory into the src/server
2) Run the command `python -m server/index.py` to start the server.

## User Configuration
### Client
1) Edit client/config.ini and change the username

### Server
- Use the TUI interface to add/edit/del users
- Manually edit the admin/data/users.csv file

## Keypairs
The keypair will be generated on the client via the TUI interface. The public key must
be located on the server prior to connection, else the server will not be able to
authenticate the client. There are several ways to transfer the keys
- Using a secure protocol, such as via SSH
- Physically, such as via USB
