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
            temperature=0.02
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error with LLM request: {e}"

def handle_with_llm(self, command_name, command, client_ip):
    prompt = f"Simulate the behavior of the '{command_name}' command with arguments: {' '.join(command)}."
    return self.fetch_llm_response(prompt)

