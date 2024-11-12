import paramiko
import socket
import threading
from data.attack_commands import CommandHandler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SSHServer(paramiko.ServerInterface):
    def __init__(self, api_key):
        self.event = threading.Event()  # Use threading.Event instead of paramiko.Event
        self.command_handler = CommandHandler(api_key=api_key)  # Initialize CommandHandler with API key

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

def start_ssh_server(api_key, host="0.0.0.0", port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    logging.info(f"SSH server running on {host}:{port}...")

    while True:
        client, addr = sock.accept()
        logging.info(f"Connection from {addr} received.")
        transport = paramiko.Transport(client)
        transport.add_server_key(paramiko.RSAKey.generate(2048))
        
        server = SSHServer(api_key=api_key)
        transport.start_server(server=server)
        
        channel = transport.accept(20)
        if channel is None:
            continue

        # Handle interactive shell
        channel.send("Welcome to the honeypot SSH server!\n")
        try:
            while True:
                channel.send(" ")
                command = ""
                while not command.endswith("\n"):
                    recv = channel.recv(1024)
                    if not recv:
                        break
                    command += recv.decode("utf-8")
                command = command.strip()

                if not command:
                    continue

                if command.lower() == "exit":
                    channel.send("logout\n")
                    break

                # Use CommandHandler to execute command
                try:
                    action, response = server.command_handler.execute(command, addr[0])

                    # Format response for realistic output
                    if response:
                        response_lines = response.strip().split("\n")
                        for line in response_lines:
                            channel.send(line + "\n")

                    channel.send(" ")
                except Exception as e:
                    logging.error(f"Error processing command '{command}': {e}")
                    channel.send("Error processing command. Please try again.\n")

        except Exception as e:
            logging.error(f"Error in client interaction: {e}")
        finally:
            channel.close()
            client.close()
            logging.info(f"Connection with {addr} closed.")