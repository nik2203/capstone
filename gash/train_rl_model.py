# train_rl_model.py
import os
from main.rl_agent import RLTrainer

if __name__ == "__main__":
    # Ensure command_list is populated correctly
    command_list = os.listdir('data/attack_commands')
    print(f"Command list for training: {command_list}")
    print(f"Total commands: {len(command_list)}")

    trainer = RLTrainer(command_list)
    trainer.train(episodes=500)
    trainer.save_model("models/saved_model.pth")
    print("Model training complete and saved to 'models/saved_model.pth'")