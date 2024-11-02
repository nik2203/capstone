# environment/honeypot_env.py

import random
import numpy as np
import logging

# Set up the logger
def setup_logger(log_file='honeypot_interactions.log'):
    logger = logging.getLogger('HoneypotLogger')
    logger.setLevel(logging.INFO)

    # Check if handlers are already added to avoid duplicate logs
    if not logger.handlers:
        # Create a file handler to log into the specified file
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Define the logging format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    return logger

# Initialize logger at the start of the file
logger = setup_logger()

class HoneypotEnv:
    def __init__(self, command_list):
        self.actions = ["allow", "block", "delay", "fake", "insult"]
        self.state_size = len(command_list)
        self.command_list = command_list
        self.current_command = None
        self.connected = True

    def reset(self):
        self.current_command = random.choice(self.command_list)
        self.connected = True

        # Log the reset state
        logger.info(f"Environment reset. Starting command: {self.current_command}")

        return self._get_state()

    def step(self, action):
        if not self.connected:
            logger.info("Attempted step while disconnected.")
            return self._get_state(), -10, True  # Penalty for disconnection

        # Validate the action index
        if action < 0 or action >= len(self.actions):
            logger.error(f"Invalid action index: {action}")
            return self._get_state(), -20, True  # Penalize for invalid action

        action_taken = self.actions[action]
        command = self.current_command
        reward = 0  # Default reward

        # Basic action rewards and penalties
        if action_taken == "block":
            reward = -1  # Small penalty for blocking, attacker is still connected
        elif action_taken == "delay":
            reward = 2  # Delay but keep connected
        elif action_taken == "fake":
            reward = 5  # Fake an action, considered effective
        elif action_taken == "insult":
            reward = 3  # Insult could provoke but keeps them connected
        else:  # Allow
            reward = 0  # Neutral action

        # Command-specific handling
        if command in ["rm", "pkill", "userdel", "iptables", "kill", "shutdown", "reboot"]:
            if action_taken == "block":
                reward += 10  # Higher reward for blocking critical commands
            else:
                reward -= 5  # Penalty for not blocking critical commands
        elif command in ["ssh-agent", "ssh-keygen", "sshd", "scp"]:
            if action_taken == "delay":
                reward += 5  # Reward for delaying SSH-related commands
            else:
                reward -= 2  # Penalty for not delaying
        elif command in ["chmod", "chown", "traceroute", "ifconfig", "ipaddr", "dig", "nslookup"]:
            if action_taken == "fake":
                reward += 5  # Reward for faking network-related commands
            else:
                reward -= 3  # Penalty for not faking
        elif command in ["userdel", "shutdown", "reboot", "su", "killall"]:
            if action_taken == "insult":
                reward += 5  # Reward for using insult on system commands
            else:
                reward -= 2  # Penalty for not using insult

        # Apply penalty for suboptimal "fake" use in critical command scenarios
        if command in ["rm", "shutdown", "reboot", "kill"] and action_taken == "fake":
            reward -= 10  # Heavier penalty for inappropriately faking critical commands

        # Cap rewards to limit variability
        reward = min(max(reward, -20), 20)  # Clipping rewards to the range [-20, 20]

        # Attacker disconnects based on random chance
        if random.random() < 0.05:  # Small chance of disconnection each step
            self.connected = False
            logger.info(f"Attacker disconnected during interaction with command '{command}'.")
            return self._get_state(), -10, True  # Penalty if attacker disconnects

        # Log the interaction details
        logger.info(f"Command: {command}, Action Taken: {action_taken}, Reward: {reward}, Connection Status: {'Connected' if self.connected else 'Disconnected'}")

        return self._get_state(), reward, not self.connected

    def _get_state(self):
        return np.array([1 if cmd == self.current_command else 0 for cmd in self.command_list])
