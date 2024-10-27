import random
import numpy as np

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
        return self._get_state()

    def step(self, action):
        if not self.connected:
            return self._get_state(), -10, True  # Penalty for disconnection

        action_taken = self.actions[action]
        command = self.current_command
        
        # Block should not disconnect unless the attacker disconnects themselves
        if action_taken == "block":
            reward = -1
        elif action_taken == "delay":
            reward = 3  # Increase reward for delay
        elif action_taken == "fake":
            reward = 2  # Reduce reward for fake to avoid overuse
        elif action_taken == "insult":
            reward = 1  # Reduce reward for insult
        else:  # Allow
            reward = 0

        # Command-specific handling
        if command in ["rm", "pkill", "userdel", "iptables", "kill", "shutdown", "reboot"]:
            if action_taken == "block":
                reward += 15  # Higher reward for blocking critical commands
            else:
                reward -= 7  # Stronger penalty for not blocking
        elif command in ["ssh-agent", "ssh-keygen", "sshd", "scp"]:
            if action_taken == "delay":
                reward += 8  # Increased reward for delaying SSH-related commands
            else:
                reward -= 3  # Penalty for not delaying
        elif command in ["chmod", "chown", "traceroute", "ifconfig", "ipaddr", "dig", "nslookup"]:
            if action_taken == "fake":
                reward += 3  # Lower reward for faking to discourage overuse
            else:
                reward -= 3
        elif command in ["userdel", "shutdown", "reboot", "su", "killall"]:
            if action_taken == "insult":
                reward += 2  # Lower reward for insult
            else:
                reward -= 2

        # Attacker disconnects based on random chance
        if random.random() < 0.05:
            self.connected = False
            return self._get_state(), -10, True

        return self._get_state(), reward, not self.connected

    def _get_state(self):
        return np.array([1 if cmd in self.current_command else 0 for cmd in self.command_list])
import random
import numpy as np

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
        return self._get_state()

    def step(self, action):
        if not self.connected:
            return self._get_state(), -10, True  # Penalty for disconnection

        action_taken = self.actions[action]
        command = self.current_command

        # Command-specific handling
        if action_taken == "block":
            reward = -1
        elif action_taken == "delay":
            reward = 2
        elif action_taken == "fake":
            reward = 5
        elif action_taken == "insult":
            reward = 3
        else:
            reward = 0  # Neutral action

        if command in ["rm", "pkill", "userdel", "iptables", "kill", "shutdown", "reboot"]:
            if action_taken == "block":
                reward += 10
            else:
                reward -= 5
        elif command in ["ssh-agent", "ssh-keygen", "sshd", "scp"]:
            if action_taken == "delay":
                reward += 5
            else:
                reward -= 2
        elif command in ["chmod", "chown", "traceroute", "ifconfig", "ipaddr", "dig", "nslookup"]:
            if action_taken == "fake":
                reward += 5
            else:
                reward -= 3
        elif command in ["userdel", "shutdown", "reboot", "su", "killall"]:
            if action_taken == "insult":
                reward += 5
            else:
                reward -= 2

        if random.random() < 0.05:
            self.connected = False
            return self._get_state(), -10, True

        return self._get_state(), reward, not self.connected

    def _get_state(self):
        return np.array([1 if cmd in self.current_command else 0 for cmd in self.command_list])
