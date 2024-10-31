import os
import yaml
import openai

openai.api_key = os.getenv("API_KEY")

def fetch_llm_response(self, prompt):
    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=prompt,
            max_tokens=100,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error with LLM request: {e}"

def handle_with_llm(self, command_name, command, client_ip):
    prompt = f"Simulate the behavior of the '{command_name}' command with arguments: {' '.join(command)}."
    return self.fetch_llm_response(prompt)

history = open("history.txt", "a+", encoding="utf-8")

if os.stat('history.txt').st_size == 0:
    with open('personalitySSH.yml', 'r', encoding="utf-8") as file:
        identity = yaml.safe_load(file)

    identity = identity['personality']

    prompt = identity['prompt']

else:
    history.write("\nHere the session stopped. Now you will start it again from the beginning with the same user. You must respond just with starting message and nothing more. " +
                    "Make sure you use same file and folder names. Ignore date-time in <>. This is not your concern.\n")
    history.seek(0)
    prompt = history.read()
