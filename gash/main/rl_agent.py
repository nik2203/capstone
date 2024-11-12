import torch
import numpy as np
import matplotlib.pyplot as plt
from models.dqn_model import DQNAgent
from environment.honeypot_env import HoneypotEnv
from data.attack_commands import CommandHandler  # Import CommandHandler
import random

class RLTrainer:
    def __init__(self, command_list, api_key):
        """
        Initialize the RLTrainer with the list of commands.
        """
        # Initialize state and action size
        self.state_size = len(command_list)
        self.action_size = 5  # Actions: allow, block, delay, fake, insult

        # Initialize CommandHandler and pass it to the HoneypotEnv
        self.command_handler = CommandHandler(api_key)
        self.env = HoneypotEnv(command_list, self.command_handler)

        # Initialize DQNAgent
        self.agent = DQNAgent(self.state_size, self.action_size)

    def train(self, episodes):
        """
        Train the RL agent for a specified number of episodes.
        """
        episode_rewards = []
        action_count = {i: 0 for i in range(self.action_size)}  # Track action distribution

        for e in range(episodes):
            # Reset environment and initialize state
            state = torch.FloatTensor(self.env.reset()).unsqueeze(0)
            total_reward = 0

            for _ in range(500):  # Limit steps per episode
                # Get action from the agent
                action = self.agent.act(state)
                action_idx = action.item()
                action_count[action_idx] += 1

                # Take step in the environment
                next_state, reward, done, info = self.env.step(action_idx)
                next_state = torch.FloatTensor(next_state).unsqueeze(0)
                total_reward += reward

                # Train the agent with the collected experience
                self.agent.train(state, action, reward, next_state, done)

                # Update the current state
                state = next_state
                if done:
                    break

            # Log the episode's reward and progress
            episode_rewards.append(total_reward)
            print(f"Episode {e + 1}/{episodes} finished with total reward: {total_reward}")

        # Plot results and action distribution
        self.plot_rewards(episode_rewards)
        self.plot_moving_average(episode_rewards, window_size=100)
        self.print_action_distribution(action_count)

        self.save_model(path="saved_model.pth")
        print("Model saved after training.")

    def save_model(self, path="saved_model.pth"):
        """
        Save the trained model to a file.
        """
        torch.save(self.agent.model.state_dict(), path)
        print(f"Model saved to {path}")

    def load_model(self, path="saved_model.pth"):
        """
        Load a pre-trained model from a file.
        """
        try:
            checkpoint = torch.load(path)
            self.agent.model.load_state_dict(checkpoint)
            print(f"Model loaded from {path}")
        except RuntimeError as e:
            print(f"Error loading model: {e}")
            print("Attempting partial load for mismatched weights.")
            model_dict = self.agent.model.state_dict()
            partial_weights = {k: v for k, v in checkpoint.items() if k in model_dict and v.size() == model_dict[k].size()}
            model_dict.update(partial_weights)
            self.agent.model.load_state_dict(model_dict)
            print("Partial weights loaded successfully.")

    def plot_rewards(self, rewards):
        """
        Plot the total rewards per episode.
        """
        plt.plot(rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Total Reward per Episode')
        plt.show()

    def plot_moving_average(self, rewards, window_size):
        """
        Plot the moving average of rewards over a specified window size.
        """
        avg_rewards = np.convolve(rewards, np.ones(window_size) / window_size, mode='valid')
        plt.plot(avg_rewards)
        plt.xlabel('Episode')
        plt.ylabel(f'Average Reward (Last {window_size} Episodes)')
        plt.title(f'Moving Average of Rewards (Window size: {window_size})')
        plt.show()

    def print_action_distribution(self, action_count):
        """
        Print the distribution of actions taken by the RL agent.
        """
        actions = ["allow", "block", "delay", "fake", "insult"]
        print("\nAction Distribution:")
        for i, count in action_count.items():
            print(f"Action '{actions[i]}': {count} times")