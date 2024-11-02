from main.rl_agent import RLTrainer
import os

if __name__ == "__main__":
    # Load the training commands
    command_list = os.listdir('data/attack_commands')

    # Initialize and train the RL model
    trainer = RLTrainer(command_list)
    trainer.train(episodes=500)

    # Validation / Testing Phase
    print("\nStarting validation...")

    # Load unseen commands for validation
    unseen_command_list = os.listdir('data/unseen_commands')  # Assuming unseen commands are stored here

    # Initialize a new trainer for validation (using the same agent but different commands)
    validation_trainer = RLTrainer(unseen_command_list)

    # Test for a smaller number of episodes (no training, just test the trained model)
    validation_trainer.train(episodes=100)  # No further training, just testing
