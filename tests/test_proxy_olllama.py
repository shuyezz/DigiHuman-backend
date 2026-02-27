import requests
import json
import subprocess


import requests

class GPT:
    BASE_URL = 'http://127.0.0.1:11434'

    def __init__(self, model_name):
        self.model_name = model_name
        #subprocess.run(["ollama", "serve"])

    def answer(self, prompt):
        url = f'{self.BASE_URL}/api/generate'
        
        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'system':  None, 
            'template':  None, 
            'context':  None, 
            'options':  None,
            'stream': False
        }

        response = requests.post(url, json=payload)

        if not response.ok:
            raise Exception('Failed to fetch response')

        response_json = response.json()
        print(response_json);
        return response_json.get('response')

if __name__ == "__main__":
    gpt = GPT("qwen2.5");
    print(gpt.answer("你好"));