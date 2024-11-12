from .fs import FileSystemCommands, HoneyPotFilesystem, T_DIR, T_FILE, T_LINK
from .net import NetworkCommands
from .sys import SystemCommands
from .package import PackageCommands
from .utility import UtilityCommands
from config.openai_config import OpenAIConfig
from utils.contextmgr import SessionContext
import torch
import time
import yaml
import logging

__all__ = ["FileSystemCommands", "NetworkCommands", "SystemCommands", "PackageCommands", "UtilityCommands"]

class CommandHandler:
    def __init__(self, api_key, delay_time=2, enable_logging=False):
        # Initialize RL model
        self.commands = {}
        self.api_key = api_key
        self.delay_time = delay_time
        self.enable_logging = enable_logging
        
        # Add OpenAI API and session context
        self.openai_config = OpenAIConfig(api_key)
        self.session_context = SessionContext()
        self.personality = self.load_personality("utils/personality.yml")

        # Set up initial state and virtual filesystem
        self.cwd = "/"
        self.filesystem = self.initialize_filesystem()
        self.state = {"cwd": self.cwd, "filesystem": self.filesystem}

        # Initialize command groups with shared state
        self.filesystem_commands = FileSystemCommands(self.filesystem, self.cwd)
        self.network_commands = NetworkCommands(self.filesystem, self.cwd)
        self.system_commands = SystemCommands(self.state)
        self.package_commands = PackageCommands(self.state)
        self.utility_commands = UtilityCommands(self.state)

        # Aggregate all commands into a single dictionary
        self.commands.update(self.filesystem_commands.commands)
        self.commands.update(self.network_commands.commands)
        self.commands.update(self.system_commands.commands)
        self.commands.update(self.package_commands.commands)
        self.commands.update(self.utility_commands.commands)

        # Rule-based harmless commands
        self.rule_based_allow = [
            "ls", "ls -l", "ls -a", "cd", "mkdir", "rmdir", "touch", "cp", "mv", "rm",
            "find", "basename", "dirname", "pwd", "cat", "head", "tail", "echo", "clear",
            "history", "sort", "uniq", "wc", "tee", "uname", "hostname", "whoami", "w",
            "who", "uptime", "id", "date", "free", "df", "nano", "vi", "less", "more",
            "yes", "bash", "sh", "exit", "logout", "nohup"
        ]

    # RL trainer will be set after initialization to avoid circular dependency
        self.rl_trainer = None

    def set_rl_trainer(self, rl_trainer):
        """Set the RLTrainer instance after initialization to avoid circular dependency."""
        self.rl_trainer = rl_trainer

    def load_personality(self, path):
        """Load system personality traits from a YAML file."""
        with open(path, "r") as file:
            data = yaml.safe_load(file)
        return data.get("personality", {}).get("prompt", "")

    def execute(self, command, client_ip):
        cmd_parts = command.strip().split()
        cmd = cmd_parts[0] if cmd_parts else ''
        
        logging.info(f"Processing command: {cmd} from IP: {client_ip}")

        if cmd in self.commands:
            if cmd in self.rule_based_allow:
                logging.info(f"Rule-based decision: Always allow command '{cmd}'.")
                return "allow", self.commands[cmd](cmd_parts, client_ip)


            action = self.get_rl_model_decision(cmd)
            static_response = self.commands[cmd](cmd_parts, client_ip)
            logging.info(f"RL Model action: {action}, Static response: {static_response}")

            if action in ["delay", "fake"]:
                prompt = self.create_prompt(cmd, static_response)
                dynamic_response = self.openai_config.get_dynamic_response(prompt)
                logging.info(f"Dynamic response: {dynamic_response}")
                return action, dynamic_response

            return action, static_response
        else:
            return "not_found", f"-bash: {command}: command not found\n"

    
    def reset_context(self):
        self.session_context.reset_context()

    def get_rl_model_decision(self, cmd):
        """
        Obtain the RL model's action based on the command's state representation.
        """
        state = self.get_state_for_command(cmd)
        state_tensor = torch.tensor(state, dtype=torch.float32)  # Convert list to tensor
        action = self.rl_trainer.agent.act(state_tensor.unsqueeze(0)).item()  # Unsqueeze after converting to tensor
        return action

    def get_state_for_command(self, cmd):
        """
        Generate a state vector for the RL model, where the target command is represented with a binary vector.
        """
        return [1 if c == cmd else 0 for c in self.commands]

    def handle_action(self, action, cmd, cmd_parts, client_ip):
        actions = ["allow", "block", "delay", "fake", "insult"]
        action_name = actions[action]

        if action_name == "allow":
            return self.commands[cmd](cmd_parts, client_ip)
        elif action_name == "block":
            return f"{cmd}: Permission denied"
        elif action_name in ["delay", "fake"]:
            if action_name == "delay":
                time.sleep(self.delay_time)
            return self.get_dynamic_openai_response(cmd, cmd_parts, client_ip)
        elif action_name == "insult":
            return "Nice try."

    def get_dynamic_openai_response(self, cmd, cmd_parts, client_ip):
        try:
            static_response = self.commands[cmd](cmd_parts, client_ip)
            prompt = self.create_prompt(cmd, static_response)
            return self.openai_config.get_dynamic_response(prompt)
        except Exception as e:
            logging.error(f"Error generating dynamic response for '{cmd}': {e}")
            return "Error processing the command dynamically."

    def create_prompt(self, command, static_response):
        if not self.personality:
            logging.error("Personality not loaded. Check the YAML file.")
            return f"Error: Personality data missing."

        if not self.session_context.has_personality():
            self.session_context.set_personality(self.personality)

        context = self.session_context.get_context()
        prompt = (
            f"System Personality:\n{self.session_context.get_personality()}\n\n"
            f"Session Context:\n{context}\n\n"
            f"Command: {command}\n"
            f"Static Response: {static_response}\n\n"
            f"Provide a realistic and context-aware response."
        )
        return prompt

    def log_command(self, command, client_ip, action, response):
        """
        Log command details including the command issued, client IP, RL action, and response sent.
        """
        actions = ["allow", "block", "delay", "fake", "insult"]
        action_name = actions[action]
        with open("honeypot_log.txt", "a") as log_file:
            log_file.write(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Client IP: {client_ip}\n"
                f"Command: {command}\nAction: {action_name}\nResponse: {response}\n\n"
            )

    def initialize_filesystem(self):
        """
        Initialize the virtual filesystem with a sample structure.
        """
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