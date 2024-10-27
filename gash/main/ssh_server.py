# main/ssh_server.py

from config.ssh_config import start_ssh_server

if __name__ == "__main__":
    channel = start_ssh_server()
    print("SSH Server running and listening on port 2222.")
