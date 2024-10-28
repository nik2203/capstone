import torch
import numpy as np
import matplotlib.pyplot as plt
from models.dqn_model import DQNAgent
from environment.honeypot_env import HoneypotEnv

class RLTrainer:
    def __init__(self, command_list):
        self.state_size = len(command_list)
        self.action_size = 5
        self.env = HoneypotEnv(command_list)
        self.agent = DQNAgent(self.state_size, self.action_size)

    def train(self, episodes):
        episode_rewards = []
        action_count = {i: 0 for i in range(self.action_size)}

        for e in range(episodes):
            state = self.env.reset()
            total_reward = 0

            for time in range(500):
                action = self.agent.act(state)
                action_count[action] += 1

                next_state, reward, done = self.env.step(action)
                total_reward += reward

                self.agent.train(state, action, reward, next_state, done)

                state = next_state
                if done:
                    break

            episode_rewards.append(total_reward)
            print(f"Episode {e + 1}/{episodes} finished with total reward: {total_reward}")

        self.plot_rewards(episode_rewards)
        self.plot_moving_average(episode_rewards, window_size=100)
        self.print_action_distribution(action_count)

    def plot_rewards(self, rewards):
        plt.plot(rewards)
        plt.xlabel('Episode')
        plt.ylabel('Total Reward')
        plt.title('Total Reward per Episode')
        plt.show()

    def plot_moving_average(self, rewards, window_size):
        avg_rewards = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
        plt.plot(avg_rewards)
        plt.xlabel('Episode')
        plt.ylabel(f'Average Reward (Last {window_size} Episodes)')
        plt.title(f'Moving Average of Rewards (Window size: {window_size})')
        plt.show()

    def print_action_distribution(self, action_count):
        actions = ["allow", "block", "delay", "fake", "insult"]
        print("\nAction Distribution:")
        for i, count in action_count.items():
            print(f"Action '{actions[i]}': {count} times")