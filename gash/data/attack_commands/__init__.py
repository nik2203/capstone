# command/__init__.py

from .fs import FileSystemCommands, HoneyPotFilesystem, T_DIR, T_FILE, T_LINK
from .net import NetworkCommands
from .sys import SystemCommands
from .package import PackageCommands
from .utility import UtilityCommands
from .malware import MalwareCommands

import time  # Ensure you have necessary imports

__all__ = [
    "FileSystemCommands", "NetworkCommands", "SystemCommands",
    "PackageCommands", "UtilityCommands", "MalwareCommands"
]

class CommandHandler:
    def __init__(self):
        self.commands = {}

        # Initialize shared state
        self.state = {
            'cwd': "/",  # Current working directory
            'filesystem': self.initialize_filesystem(),
            'commands': self.commands
        }

        # Initialize command groups with shared state
        self.filesystem_commands = FileSystemCommands(self.state)
        self.network_commands = NetworkCommands(self.state)
        self.system_commands = SystemCommands(self.state)
        self.package_commands = PackageCommands(self.state)
        self.utility_commands = UtilityCommands(self.state)
        self.malware_commands = MalwareCommands(self.state)

        # Aggregate all commands into a single dictionary
        self.commands.update(self.filesystem_commands.commands)
        self.commands.update(self.network_commands.commands)
        self.commands.update(self.system_commands.commands)
        self.commands.update(self.package_commands.commands)
        self.commands.update(self.utility_commands.commands)
        self.commands.update(self.malware_commands.commands)

    def initialize_filesystem(self):
        # Initialize the virtual filesystem here
        fs_structure = [
            '/', T_DIR, 0, 0, 4096, 0o755, time.time(), [
                ['home', T_DIR, 0, 0, 4096, 0o755, time.time(), [
                    ['user', T_DIR, 1000, 1000, 4096, 0o755, time.time(), [], None, None],
                ], None, None],
                ['etc', T_DIR, 0, 0, 4096, 0o755, time.time(), [
                    ['passwd', T_FILE, 0, 0, 1024, 0o644, time.time(), [], None, None],
                ], None, None],
                ['var', T_DIR, 0, 0, 4096, 0o755, time.time(), [], None, None],
                ['tmp', T_DIR, 0, 0, 4096, 0o777, time.time(), [], None, None],
            ], None, None
        ]
        return HoneyPotFilesystem(fs_structure)

    def execute(self, command, client_ip):
        cmd_parts = command.strip().split()
        cmd = cmd_parts[0] if cmd_parts else ''
        if cmd in self.commands:
            # Execute the command
            result = self.commands[cmd](cmd_parts, client_ip)
            # Update shared state
            self.state['cwd'] = self.filesystem_commands.cwd  # Update cwd
            return result
        else:
            return f"-bash: {command}: command not found\n"