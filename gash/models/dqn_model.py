import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque

class DQNModel(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQNModel, self).__init__()
        self.fc1 = nn.Linear(11, 128)
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

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.0001)
        self.criterion = nn.MSELoss()
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.gamma = 0.99
        self.memory = deque(maxlen=20000)
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
        
        minibatch = random.sample(self.memory, self.batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward + self.gamma * torch.max(self.target_model(next_state)).item() * (1 - done)
            target = torch.tensor([[target]], dtype=torch.float32)
            current_q = self.model(state)[0][action].view(1, 1)
            
            loss = self.criterion(current_q, target)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_model(self, path="saved_model.pth"):
        torch.save(self.model.state_dict(), path)

    def load_model(self, path="saved_model.pth"):
        self.model.load_state_dict(torch.load(path))
        self.update_target_network()  # Update target model to match the loaded model

    def replay(self):
        """Prints Q-values for the current memory for debugging purposes."""
        print("Replay Memory Sample Q-values:")
        for state, action, _, _, _ in self.memory:
            q_values = self.model(state)
            print("Q-values:", q_values)