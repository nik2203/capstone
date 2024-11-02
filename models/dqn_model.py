# models/dqn_model.py

import torch
import torch.nn as nn
import torch.optim as optim
import random
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
        self.update_target_network()

        # Hyperparameters
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.00025)  # Reduced learning rate for stability
        self.criterion = nn.MSELoss()
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.95
        self.memory = deque(maxlen=2000)
        self.batch_size = 64

    def update_target_network(self):
        self.target_model.load_state_dict(self.model.state_dict())

    def act(self, state):
        if random.random() < self.epsilon:
            return torch.tensor([[random.randrange(self.action_size)]])
        else:
            with torch.no_grad():
                return torch.argmax(self.model(state)).unsqueeze(0)

    def train(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
        if len(self.memory) < self.batch_size:
            return
        
        # Sample mini-batch from experience replay buffer
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_q_values = self.target_model(next_state)
                target = reward + self.gamma * torch.max(next_q_values).item()

            # Ensure target is (1, 1) to match current_q's shape
            target = torch.tensor([[target]], dtype=torch.float32)
            current_q = self.model(state)[0][action].view(1, 1)
            
            # Calculate loss
            loss = self.criterion(current_q, target)
            
            # Optimize the model
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        # Update epsilon for exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Update target model periodically
        if done:
            self.update_target_network()

    def replay(self):
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_q_values = self.target_model(next_state)
                target = reward + self.gamma * torch.max(next_q_values).item()

            # Ensure target is (1, 1) to match current_q's shape
            target = torch.tensor([[target]], dtype=torch.float32)
            current_q = self.model(state)[0][action].view(1, 1)
            
            # Calculate loss
            loss = self.criterion(current_q, target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()