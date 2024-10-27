import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

class DQNModel(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNModel, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.model = DQNModel(state_size, action_size)
        self.target_model = DQNModel(state_size, action_size)
        self.update_target_model()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0003)  # Reduced learning rate for smoother training
        self.criterion = nn.MSELoss()
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995  # Faster decay rate to encourage earlier exploitation
        self.batch_size = 64  # Larger batch size for stability
        self.target_update_freq = 10  # More frequent updates to the target model

    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        else:
            state = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                return torch.argmax(self.model(state)).item()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        batch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in batch:
            target = self.model(torch.FloatTensor(state)).detach().clone()
            
            if done:
                target[action] = reward
            else:
                next_q_values = self.target_model(torch.FloatTensor(next_state)).detach()
                next_action = torch.argmax(self.model(torch.FloatTensor(next_state))).item()
                target[action] = reward + self.gamma * next_q_values[next_action].item()

            # Optimize the model
            output = self.model(torch.FloatTensor(state))[action]
            loss = self.criterion(output, target[action])
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def train(self, state, action, reward, next_state, done):
        self.remember(state, action, reward, next_state, done)
        self.replay()

        # Update target network after every N episodes
        if done and (len(self.memory) % self.target_update_freq == 0):
            self.update_target_model()