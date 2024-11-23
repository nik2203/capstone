from openai import OpenAI
import logging
import yaml
import os

# Move the client creation inside the class
class OpenAIConfig:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)  # Create client instance with API key
    
    def load_personality(self):
        # Correct the file path to make sure it's correctly pointing to the location of personality.yml
        base_path = os.path.dirname(os.path.abspath(__file__))
        personality_path = os.path.join(base_path, '..', 'utils', 'personality.yml')
        
        # Debugging: print the exact path to verify it's correct
        print(f"Loading personality from: {personality_path}")  # Debugging print
        
        try:
            with open(personality_path, 'r') as file:
                personality_data = yaml.safe_load(file)
            
            # Debugging print to check what is being loaded
            print(f"Personality data loaded: {personality_data}")

            return personality_data.get("personality", {}).get("prompt", "")
        except FileNotFoundError:
            print(f"Error: The file {personality_path} was not found.")
            return ""
        except Exception as e:
            print(f"Error loading personality file: {e}")
            return ""

    def get_dynamic_response(self, prompt):
        try:
            personality = self.load_personality()
            if not personality:
                print("Error: No personality loaded.")
                return "Error: No personality loaded."

            print(f"Using personality: {personality}")  # Debugging print
            print(f"User prompt: {prompt}")  # Debugging print
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": personality},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800
            )
            raw_output = response.choices[0].message.content  # Added .content to get the string
            formatted_output = self.clean_output(raw_output)
            return formatted_output
        except Exception as e:
            logging.error(f"Error fetching dynamic response: {e}")
            return f"Error fetching dynamic response: {e}"

    @staticmethod
    def clean_output(output):
        unwanted_lines = ["plaintext", "bash", "Last login", "Welcome to Ubuntu"]
        for line in unwanted_lines:
            output = output.replace(line, "").strip()

        # Further clean up to avoid any extraneous lines
        cleaned = "\n".join([line for line in output.splitlines() if line.strip()])
        cleaned = output.replace("```", "").strip()
        return cleaned