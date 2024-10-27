# config/ssh_config.py

import paramiko
import socket

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = paramiko.Event()
    
    def check_auth_password(self, username, password):
        # Accept all credentials for the honeypot
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

def start_ssh_server(host="0.0.0.0", port=2222):
    # Initialize SSH server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(100)
    
    client, addr = sock.accept()
    transport = paramiko.Transport(client)
    transport.add_server_key(paramiko.RSAKey.generate(2048))
    
    server = SSHServer()
    transport.start_server(server=server)
    
    channel = transport.accept(20)
    if channel is None:
        raise Exception("No channel")
    return channel
