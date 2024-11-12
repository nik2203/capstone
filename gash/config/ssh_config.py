import paramiko
import socket
import threading
from data.attack_commands import CommandHandler

class SSHServer(paramiko.ServerInterface):
    def __init__(self, api_key):
        self.event = threading.Event()
        self.command_handler = CommandHandler(api_key=api_key)

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return "password"

    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True


def handle_client(channel, server, addr):
    cwd = "~"  # Initial directory

    try:
        # Welcome message
        channel.send("Welcome to the honeypot SSH server!\n")

        while True:
            # Send the prompt
            channel.send("$ ")

            # Receive the full command
            command = ""
            while not command.endswith("\n"):  # Accumulate input until Enter
                recv = channel.recv(1024)
                if not recv:
                    raise EOFError  # Disconnect if no input
                command += recv.decode("utf-8")

            command = command.strip()  # Clean the command
            if not command:  # Empty input
                continue

            # Handle 'exit' command
            if command.lower() == "exit":
                channel.send("logout\n")
                break

            # Handle 'cd' to update the directory
            if command.startswith("cd "):
                try:
                    cwd = server.command_handler.command_cd(command.split(), addr[0]).strip() or cwd
                except Exception as e:
                    channel.send(f"Error: {e}\n")
                continue

            # Execute other commands
            try:
                action, response = server.command_handler.execute(command, addr[0])
                if response:
                    channel.send(response.strip() + "\n")
            except Exception as e:
                channel.send(f"Error processing command: {e}\n")
                print(f"Error processing command '{command}': {e}")

    except EOFError:
        print(f"Client {addr} disconnected.")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        channel.close()


def start_ssh_server(api_key, host="0.0.0.0", port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    print(f"SSH server running on {host}:{port}...")

    while True:
        client, addr = sock.accept()
        print(f"Connection from {addr} received.")
        transport = paramiko.Transport(client)
        transport.add_server_key(paramiko.RSAKey.generate(2048))

        server = SSHServer(api_key=api_key)
        transport.start_server(server=server)

        channel = transport.accept(20)
        if channel is None:
            continue

        threading.Thread(target=handle_client, args=(channel, server, addr)).start()