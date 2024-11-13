import openai
import logging  # Add this import

class OpenAIConfig:
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_dynamic_response(self, prompt):
        try:
            # Use the updated API to fetch a response
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Replace with 'gpt-3.5-turbo' if needed
                messages=[
                    {"role": "system", "content": "You are a Linux terminal. Provide plain, realistic output for commands without formatting."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.02,
            )

            # Extract the content of the response
            raw_output = response["choices"][0]["message"]["content"]

            # Remove any unwanted backticks or formatting marks
            formatted_output = self.clean_output(raw_output)

            return formatted_output
        except openai.error.OpenAIError as e:
            logging.error(f"Error fetching dynamic response: {e}")
            return f"Error fetching dynamic response: {e}"
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return f"Unexpected error: {e}"

    @staticmethod
    def clean_output(output):
        """
        Remove unwanted formatting like backticks or extra newlines.
        """
        # Remove backticks and trailing spaces
        cleaned = output.replace("```", "").strip()

        # Ensure the output doesn't have unnecessary leading/trailing newlines
        return cleaned
