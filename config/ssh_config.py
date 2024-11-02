import paramiko
import socket
import threading
from data.attack_commands import CommandHandler


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()  # Use threading.Event instead of paramiko.Event
        self.command_handler = CommandHandler()  # Initialize CommandHandler to handle commands

    def check_auth_password(self, username, password):
        # Accept all credentials for testing
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

def start_ssh_server(host="0.0.0.0", port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(100)
    print(f"SSH server running on {host}:{port}...")

    while True:
        client, addr = sock.accept()
        print(f"Connection from {addr} received.")
        transport = paramiko.Transport(client)
        transport.add_server_key(paramiko.RSAKey.generate(2048))
        
        server = SSHServer()
        transport.start_server(server=server)
        
        channel = transport.accept(20)
        if channel is None:
            continue

        # Handle interactive shell
        channel.send("Welcome to the SSH server!\n")
        while True:
            try:
                channel.send("$ ")
                command = ""
                while not command.endswith("\n"):
                    recv = channel.recv(1024)
                    if not recv:
                        break
                    command += recv.decode("utf-8")
                command = command.strip()

                # Use CommandHandler to execute command
                response = server.command_handler.execute(command, addr[0])
                channel.send(response + "\n")

                if command == "exit":
                    channel.send("logout\n")
                    break
            except Exception as e:
                print(f"Error handling command: {e}")
                break

        channel.close()
        client.close()
