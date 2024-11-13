import paramiko
import socket
import threading
import logging
import os
from dotenv import load_dotenv
from data.attack_commands import CommandHandler
from datetime import datetime
from main.rl_agent import RLTrainer
import signal
import sys
from time import time

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set OPENAI_API_KEY in the .env file.")

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)
paramiko.util.log_to_file("paramiko.log")

# Graceful shutdown
def graceful_shutdown(signum, frame):
    logging.info("Shutting down SSH server gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

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
        return True

    def check_channel_shell_request(self, channel):
        return True

def log_command(client_ip, command, action, response):
    """
    Log the executed command, action, and response.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {client_ip} - Command: {command} - Action: {action} - Response: {response}\n"
    try:
        with open("honeypot.log", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        logging.error(f"Error writing to log file: {e}")

def handle_client(client_socket):
    """
    Handle an incoming SSH client connection.
    """
    client_ip = client_socket.getpeername()[0]
    transport = paramiko.Transport(client_socket)
    transport.add_server_key(paramiko.RSAKey.generate(2048))

    server = SSHServer()
    try:
        transport.start_server(server=server)
    except paramiko.SSHException as e:
        logging.error(f"SSH negotiation failed: {e}")
        return

    channel = transport.accept(20)
    if channel is None:
        logging.error("No channel.")
        transport.close()
        return

    # Load command list and initialize CommandHandler
    command_list = [f[:-3] for f in os.listdir('data/attack_commands') if f.endswith('.py') and f != "__init__.py"]
    print(f"Loaded command list: {command_list}")
    print(f"Total commands: {len(command_list)}")

    command_handler = CommandHandler(api_key=api_key)
    rl_trainer = RLTrainer(command_list, api_key=api_key)
    command_handler.set_rl_trainer(rl_trainer)

    # Load the trained model
    try:
        rl_trainer.load_model("saved_model.pth")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    client_last_command_time = {}
    start_time = datetime.now()
    logging.info(f"Session started for {client_ip} at {start_time}")

    try:
        server.event.set()
        channel.send("$ ")

        cmd_buffer = ''
        while True:
            current_time = time()
            if client_ip in client_last_command_time:
                if current_time - client_last_command_time[client_ip] < 1:  # Rate-limit to 1 command per second
                    channel.send("Too many commands. Slow down.\n")
                    continue

            data = channel.recv(1024)
            if not data:
                break

            data_decoded = data.decode('utf-8', 'ignore')
            for char in data_decoded:
                if char == '\r' or char == '\n':
                    channel.send('\r\n')
                    command = cmd_buffer.strip()
                    cmd_buffer = ''

                    if command.lower() == "exit":
                        channel.send("logout\r\n")
                        break
                    elif command:
                        action, output = command_handler.execute(command, client_ip)
                        if not output:
                            output = f"bash: {command}: command not found"

                        # Send output to the client
                        formatted_output = "\r\n".join(line.strip() for line in output.splitlines())
                        channel.send(formatted_output + "\r\n")

                        
                        # Log command and output
                        log_command(client_ip, command, action, output)
                        channel.send("$ ")
                elif char == '\b' or ord(char) == 127:
                    if len(cmd_buffer) > 0:
                        cmd_buffer = cmd_buffer[:-1]
                        channel.send('\b \b')
                elif char == '\t':  # Ignore tab completion
                    pass
                else:
                    cmd_buffer += char
                    channel.send(char)

    except EOFError:
        logging.info("Client disconnected.")
    except Exception as e:
        logging.error(f"Error: {e}", exc_info=True)
    finally:
        end_time = datetime.now()
        logging.info(f"Session ended for {client_ip} at {end_time}. Duration: {end_time - start_time}")
        if channel:
            channel.close()
        if transport:
            transport.close()

def start_ssh_server(host="0.0.0.0", port=2222):
    """
    Start the SSH server and accept incoming client connections.
    """
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