import openai

class OpenAIConfig:
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_dynamic_response(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Linux terminal simulation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error: {e}"