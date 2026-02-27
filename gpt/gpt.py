import requests
import json
import subprocess


import requests

class GPT:
    BASE_URL = 'http://127.0.0.1:11434'

    def __init__(self, model_name):
        self.model_name = model_name
        #subprocess.run(["ollama", "serve"])

    def answer_generate(self, prompt):
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
        return response_json.get('response')

    def answer_generate_streamed_response(self, prompt):

        url = f'{self.BASE_URL}/api/generate'

        payload = {
            'model': self.model_name,
            'prompt': prompt,
            'system': None,
            'template': None,
            'context': None,
            'options': None,
            'stream': True
        }

        response = requests.post(url, json=payload, stream=True)

        if not response.ok:
            raise Exception('Failed to fetch response')

        # Iterate over each line in the streaming response
        for line in response.iter_lines():
            if line:
                try:
                    json_data = json.loads(line.decode('utf-8'))
                    yield json.dumps(json_data) + "\n"
                except json.JSONDecodeError:
                    # If there's a decoding error, we simply continue
                    continue

    def answer_chat_response(self, history: list):
        url = f'{self.BASE_URL}/api/chat';
        #print(history);
        payload = {
            'model': self.model_name,
            'messages': history,
            'options': None,
            'stream': False,
        }

        response = requests.post(url, json=payload);
        if not response.ok:
            raise Exception('聊天请求发送失败。');

        response_json = response.json()
        message = response_json.get('message');
        print(message);
        return message;
        