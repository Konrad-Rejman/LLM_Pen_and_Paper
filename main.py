import ollama, os
from dotenv import load_dotenv

load_dotenv()

client = ollama.Client(host=os.getenv('HOSTURL'))

# Models: ['qwen3:32b', 'gemma3:12b', 'deepseek-r1:32b', 'gpt-oss:120b', 'llama3.1:8b', 'llama3.2:latest', 'gpt-oss:latest']
model = 'qwen3:32b'

# Get user input
input = input('Enter a starting prompt: ')
print('Input:\n' + input)

# Get response from model
response = client.chat(model=model, messages=[ 
    {'role': 'user',  'content': input}, # User input for model to respond to
    {'role': 'system',  'content': 'Act rude in your responses.'}, # Instructions to model on how to act
]) 
print('Response:\n' + response.message.content)