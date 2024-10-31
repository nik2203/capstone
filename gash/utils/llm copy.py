import os
import yaml
import openai
from datetime import datetime

# Set the OpenAI API key from environment variables
openai.api_key = os.getenv("API_KEY")


class LLMCommandHandler:
    def __init__(self):
        self.history_file = "history.txt"
        self.identity_file = "personalitySSH.yml"
        self.prompt = self.load_initial_prompt()

    def load_initial_prompt(self):
        # Check if history is empty
        if os.stat(self.history_file).st_size == 0:
            # Load personality from identity file for a fresh session
            with open(self.identity_file, 'r', encoding="utf-8") as file:
                identity = yaml.safe_load(file)
            prompt = identity['personality']['prompt']

            # Log initial prompt to history file
            with open(self.history_file, 'a+', encoding="utf-8") as history:
                history.write(prompt + "\n")
        else:
            # Load existing history as the starting prompt
            with open(self.history_file, 'r', encoding="utf-8") as history:
                prompt = history.read()
        return prompt

    def fetch_llm_response(self, prompt):
        try:
            response = openai.Completion.create(
                engine="gpt-4",
                prompt=prompt,
                max_tokens=100,
                temperature=0.02
            )
            return response.choices[0].text.strip()
        except Exception as e:
            return f"Error with LLM request: {e}"

    def handle_with_llm(self, command_name, command, client_ip):
        # Format the prompt to include command simulation request
        prompt = (self.prompt +
                  f"\nSimulate the behavior of the '{command_name}' command with arguments: {' '.join(command)}.")

        # Fetch response from LLM
        response = self.fetch_llm_response(prompt)

        # Log to history
        with open(self.history_file, 'a+', encoding="utf-8") as history:
            history.write(
                f"Command: {command_name} {command}\nResponse: {response}\n")

        return response


# Example usage
handler = LLMCommandHandler()
print(handler.handle_with_llm("ls", ["-la"], "192.168.1.1"))
