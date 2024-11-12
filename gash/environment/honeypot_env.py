import random
import numpy as np
import logging
import os

# Set up the logger
def setup_logger(log_file="honeypot_interactions.log"):
    logger = logging.getLogger("HoneypotLogger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()

class HoneypotEnv:
    def __init__(self, command_list, command_handler, history_file="session_history.pth"):
        self.actions = ["allow", "block", "delay", "fake", "insult"]
        self.state_size = len(command_list)
        self.command_list = command_list
        self.current_command = None
        self.connected = True
        self.history_file = history_file
        self.session_data = []
        self.command_handler = command_handler  # Use CommandHandler for dynamic responses

        # Ensure the history file exists
        if not os.path.exists(self.history_file):
            self.save_session_data([])

        # Always allow these harmless commands
        self.rule_based_allow = [
            "ls", "ls -l", "ls -a", "cd", "mkdir", "rmdir", "touch", "cp", "mv", "rm",
            "find", "basename", "dirname", "pwd", "cat", "head", "tail", "echo", "clear",
            "history", "sort", "uniq", "wc", "tee", "uname", "hostname", "whoami", "w",
            "who", "uptime", "id", "date", "free", "df", "nano", "vi", "less", "more",
            "yes", "bash", "sh", "exit", "logout", "nohup"
        ]

    def reset(self):
        """Reset the environment and select a new random command."""
        self.current_command = random.choice(self.command_list)
        self.connected = True
        logger.info(f"Environment reset. Starting command: {self.current_command}")
        return self._get_state()

    def step(self, action):
        """Take an action and evaluate its consequences."""
        if not self.connected:
            logger.info("Attempted step while disconnected.")
            return self._get_state(), -10, True, {"response": "Connection closed."}

        command = self.current_command.strip().split()[0]  # Extract the base command
        info = {"command_type": "rule_based" if command in self.rule_based_allow else "rl_based"}

        # Rule-based logic for harmless commands
        if command in self.rule_based_allow:
            if action != self.actions.index("allow"):
                logger.warning(f"Incorrect action {self.actions[action]} taken for harmless command '{command}'.")
                reward = -20  # Penalty for misclassifying harmless commands
            else:
                reward = 20  # Reward for correctly allowing harmless commands
            logger.info(f"Rule-based handling for harmless command: '{command}'. Action: {self.actions[action]}, Reward: {reward}")
            self.log_interaction(command, action, reward, self._get_state().tolist(), False)
            return self._get_state(), reward, False, {"response": f"Executed {command} successfully."}

        # RL-based logic for other commands
        action_taken = self.actions[action]
        reward = self.calculate_reward(command, action_taken)

        # Handle occasional disconnect
        if random.random() < 0.05:
            self.connected = False
            logger.info(f"Attacker disconnected during interaction with command '{command}'.")
            self.log_interaction(command, action, -10, self._get_state().tolist(), True)
            return self._get_state(), -10, True, {"response": "Connection closed."}

        # Log and return
        logger.info(
            f"Command: {command}, Action Taken: {action_taken}, Reward: {reward}, "
            f"Connection Status: {'Connected' if self.connected else 'Disconnected'}"
        )
        self.log_interaction(command, action, reward, self._get_state().tolist(), not self.connected)
        return self._get_state(), reward, not self.connected, info

    def calculate_reward(self, command, action_taken):
        """Calculate reward for RL-based decision-making."""
        sensitive_commands = [
            "chmod", "chown", "passwd", "useradd", "usermod", "su", "export", "set", "unset",
            "systemctl", "service"
        ]
        harmful_commands = ["shutdown", "reboot", "kill", "killall", "pkill", "crontab", "at"]
        network_commands = [
            "ping", "curl", "wget", "scp", "sftp", "ssh", "tar", "tcpdump", "nmap",
            "ifconfig", "ip", "ipaddr", "traceroute", "dig", "nslookup"
        ]
        resource_commands = [
            "uptime", "vmstat", "ps", "iostat", "htop", "free", "df", "top", "sar",
            "lscpu", "dmesg", "jobs", "bg", "fg", "watch"
        ]

        if command in sensitive_commands:
            return 15 if action_taken in ["block", "fake"] else -25
        elif command in harmful_commands:
            return 25 if action_taken in ["block", "insult"] else -30
        elif command in network_commands:
            return 15 if action_taken in ["delay", "fake"] else -20
        elif command in resource_commands:
            return 10 if action_taken in ["fake", "allow"] else -15
        else:
            # Default fallback
            return 5 if action_taken in ["allow", "fake"] else -5

    def _get_state(self):
        """Return the current state as a one-hot encoded vector."""
        return np.array([1 if cmd == self.current_command else 0 for cmd in self.command_list])

    def log_interaction(self, command, action, reward, next_state, done):
        """Log the interaction."""
        interaction_log = {
            "command": command,
            "action": self.actions[action] if action < len(self.actions) else "unknown",
            "reward": reward,
            "next_state": next_state,
            "done": done,
        }
        self.session_data.append(interaction_log)
        logger.info(f"Logged interaction: {interaction_log}")

    def save_session_data(self, data):
        """Save session data to the history file."""
        torch.save(data, self.history_file)
        logger.info(f"Saved session data to {self.history_file}.")