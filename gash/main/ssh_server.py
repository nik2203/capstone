import paramiko
import socket
import threading
import logging
from config.ssh_config import start_ssh_server
from data.attack_commands import CommandHandler
from datetime import datetime

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
paramiko.util.log_to_file("paramiko.log")

class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True  # Accept PTY requests

    def check_channel_shell_request(self, channel):
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
        transport.start_server(server=server)
    except paramiko.SSHException as e:
        logging.error(f"SSH negotiation failed: {e}")
        return

    channel = transport.accept(20)  # Increase timeout if necessary
    if channel is None:
        logging.error("No channel.")
        transport.close()
        return

    command_handler = CommandHandler()  # Initialize CommandHandler

    try:
        server.event.set()  # Signal that the shell was successfully created

        # Send initial welcome message and prompt
        channel.send("\r\nWelcome to the honeypot SSH server!\r\n")
        channel.send("$ ")

        cmd_buffer = ''
        while True:
            data = channel.recv(1024)
            if not data:
                break

            # Decode received bytes
            data_decoded = data.decode('utf-8', 'ignore')

            # Process each character
            for char in data_decoded:
                if char == '\r' or char == '\n':
                    # Echo newline to client
                    channel.send('\r\n')

                    command = cmd_buffer.strip()
                    cmd_buffer = ''  # Reset the command buffer

                    # Log the command
                    log_command(client_ip, command)

                    # Handle the command using CommandHandler
                    if command.lower() == "exit":
                        channel.send("logout\r\n")
                        break
                    else:
                        # Execute the command using CommandHandler
                        output = command_handler.execute(command, client_ip)
                        if not output:
                            output = f"bash: {command}: command not found"
                        
                        # Send output followed by a properly aligned prompt
                        channel.send(output + "\r\n")
                        channel.send("$ ")  # Prompt at the start of the new line
                elif char == '\b' or ord(char) == 127:
                    # Handle backspace/delete key
                    if len(cmd_buffer) > 0:
                        cmd_buffer = cmd_buffer[:-1]
                        # Move cursor back, overwrite the character with space, move cursor back again
                        channel.send('\b \b')
                elif char == '\t':
                    # Ignore tab characters or implement auto-completion logic
                    pass
                else:
                    cmd_buffer += char
                    # Echo the character back to the client
                    channel.send(char)

    except EOFError:
        logging.info("Client disconnected.")
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
    finally:
        if channel:
            channel.close()
        if transport:
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