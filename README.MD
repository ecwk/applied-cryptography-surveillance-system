# ACG CA2

## Prerequisites
1) Install Python 3.9 or later
2) Install required package(s) using the command `pip install -r requirements.txt`

## To Run
### Client
1) Open another new terminal window and change directory into src/client
2) Run the command `python -m src/client/index.py` to start the client.

### Server
1) Open a new terminal window and change directory into the src/server
2) Run the command `python -m src/server/index.py` to start the server.

## User Configuration
### Client
1) Edit src/client/config.ini and change the username

### Server
- Use the TUI interface to add/edit/del users
- Manually edit the src/admin/data/users.csv file

## Keypairs
The keypair will be generated on the client via the TUI interface. The public key must
be located on the server prior to connection, else the server will not be able to
authenticate the client. There are several ways to transfer the keys
- Using a secure protocol, such as via SSH
- Physically, such as via USB

## Folder Structure
### Client
`auth/` - handles api calls to authd<br/>
`controllers/` - contains flow control logic<br/>
`keys/` - contains public key pair<br/>
`util/` - conatins helper functions<br/>
`views/` - contains display data for TUI<br/>
`config.ini` - application settings<br/>
`index.py` - main application entry-point<br/>
`logs.txt` - camera logs<br/>

### Server
`auth/` - handles api requests to authd<br/>
`build/` - contain webinterface files<br/>
`data/` - contains ftp files and userlist file, users.csv<br/>
`models/` - allows access and manipulation to .csv files<br/>
`util/` - contains helper functions<br/>
`authd.py` - authorisation server logic<br/>
`ftpd.py` - ftp server logic<br/>
`httpd.py` - web interface server logic<br/>
`index.py` - main application entry-point<br/>
    

