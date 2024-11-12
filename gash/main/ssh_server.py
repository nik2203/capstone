import paramiko
import socket
import threading
import logging
from config.ssh_config import start_ssh_server
from data.attack_commands import CommandHandler
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in the .env file.")

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
paramiko.util.log_to_file("paramiko.log")


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        logging.debug(f"Channel request type: {kind}, id: {chanid}")
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        logging.debug(f"Authentication request for username: {username}")
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        logging.debug(f"PTY request: term={term}, width={width}, height={height}")
        return True  # Accept PTY requests

    def check_channel_shell_request(self, channel):
        logging.debug("Shell request received.")
        return True  # Accept shell requests


def log_command(client_ip, command):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {client_ip} - {command}\n"
    with open("honeypot.log", "a") as log_file:
        log_file.write(log_entry)


def handle_client(client_socket):
    client_ip = client_socket.getpeername()[0]
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(paramiko.RSAKey.generate(2048))

    server = SSHServer()
    try:
        logging.info("Starting SSH transport server.")
        transport.start_server(server=server)
    except paramiko.SSHException as e:
        logging.error(f"SSH negotiation failed: {e}")
        return

    try:
        logging.info("Waiting for channel.")
        channel = transport.accept(timeout=30)  # Increase timeout for client connection
        if channel is None:
            logging.error("No channel established.")
            return

        # Initialize CommandHandler
        command_handler = CommandHandler(api_key=api_key)

        # Send welcome message
        channel.send("\r\nWelcome to the honeypot SSH server!\r\n")
        channel.send("$ ")

        cmd_buffer = ''
        while True:
            data = channel.recv(1024)
            if not data:
                break

            data_decoded = data.decode('utf-8', 'ignore')

            for char in data_decoded:
                if char in ('\r', '\n'):
                    channel.send("\r\n")
                    command = cmd_buffer.strip()
                    cmd_buffer = ''
                    log_command(client_ip, command)

                    if command.lower() == "exit":
                        channel.send("logout\r\n")
                        break
                    else:
                        action, output = command_handler.execute(command, client_ip)
                        if not output:
                            output = f"bash: {command}: command not found"
                        channel.send(output + "\r\n$ ")
                elif char in ('\b', '\x7f'):
                    if len(cmd_buffer) > 0:
                        cmd_buffer = cmd_buffer[:-1]
                        channel.send('\b \b')
                else:
                    cmd_buffer += char
                    channel.send(char)

    except Exception as e:
        logging.error(f"Error handling client: {e}", exc_info=True)
    finally:
        logging.info(f"Client {client_ip} disconnected.")
        if transport.is_active():
            transport.close()

def start_ssh_server(host="0.0.0.0", port=2222):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(100)
        logging.info(f"SSH Server running on {host}:{port}...")

        while True:
            client_socket, addr = server_socket.accept()
            logging.info(f"Connection from {addr} received.")
            threading.Thread(target=handle_client, args=(client_socket,)).start()

    except Exception as e:
        logging.error(f"Error starting SSH server: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_ssh_server()