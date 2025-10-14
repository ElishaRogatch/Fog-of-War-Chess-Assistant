import json
import requests
import tkinter as tk
from tkinter import simpledialog

class InputProcessor:
    def __init__(self):
        # Hugging Face API key:
        self.api_key = "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"
        self.mistral_api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    # get structured response from Mistral:
    def get_mistral_output(self, user_input):
        prompt = (
            "You are a helpful assistant. Respond **only** in JSON format with these fields:\n"
            "1. 'severity': A score (1-5) based on urgency according to the user.\n"
            "2. 'piece': The opponent's chess piece involved.\n"
            "3. 'action': The exact desired action (counter, punish, take, analyze, etc).\n"
            "4. 'preference': Whether the user is saying directly that the opponent overuses the piece (true/false).\n"
            "5. 'force forks': Whether the user is saying directly that the opponent tries to force forks (true/false).\n"
            f"User input: {user_input}\n\n"
            "Respond **ONLY** with a valid JSON object, with no extra text, explanations, or greetings."
        )

        data = {"inputs": prompt}
        response = requests.post(self.mistral_api_url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            raw_output = result[0]["generated_text"].strip() if result else None

            if not raw_output:
                print("Warning: Empty response from Mistral")
                return None

            # print("Raw Mistral Output:", raw_output)  # for debugging
            return self.extract_json(raw_output)
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None

    # extracts only the JSON portion from Mistral's response:
    def extract_json(self, response_text):
        """
        Removes unnecessary text and extracts only the JSON portion.
        """
        try:
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end == -1:
                print("Warning: No valid JSON found in Mistral's response.")
                return None

            json_string = response_text[json_start:json_end]
            return json_string.strip()
        except Exception as e:
            print(f"JSON Extraction Error: {e}")
            return None

    # parses JSON:
    def parse_structured_data(self, json_string):
        """
        Parses the extracted JSON safely.
        """
        try:
            if json_string:
                data_dict = json.loads(json_string)

                formatted_dict = {
                    "severity": int(data_dict.get("severity", 0)),
                    "piece": str(data_dict.get("piece", "")),
                    "action": str(data_dict.get("action", "")),
                    "preference": bool(data_dict.get("preference", False)),
                    "force forks": bool(data_dict.get("force forks", False)),
                }
                return formatted_dict
            else:
                print("Warning: No valid JSON string provided for parsing.")
                return None
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw JSON String: {json_string}")
            return None

    def bias(self):
        root = tk.Tk()
        root.withdraw()
        input_value = simpledialog.askstring("Input", "Hello, what would you like me to do:")
        if input_value:
            print("User input:", input_value)
            result = self.main(input_value)
            return result
        else:
            print("No input provided.")
            return None

    def main(self, user_input):
        output_str = self.get_mistral_output(user_input)

        if output_str:
            return self.parse_structured_data(output_str)
        else:
            print("No valid output received from Mistral.")
            return None


if __name__ == "__main__":
    processor = InputProcessor()
    result = processor.bias()

    if result:
        print('\n', "Processed Output:", result, '\n')
    else:
        print("Failed to obtain valid processed output.")
