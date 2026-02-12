import ollama, os
from dotenv import load_dotenv

load_dotenv()

client = ollama.Client(host=os.getenv('HOSTURL'))

# Models: ['qwen3:32b', 'gemma3:12b', 'deepseek-r1:32b', 'gpt-oss:120b', 'llama3.1:8b', 'llama3.2:latest', 'gpt-oss:latest']
model = 'gpt-oss:120b'

# Game start
print('Press ctrl + c to exit.')
print('The LLM will act as the Game Master, play along by inputing your characters actions each turn and the LLM will respond with the outcome setting up the next turn.')
print('Generating...')

rules = {'role': 'system', 'content': 'Act as the GameMaster for the following pen and paper game, with the user acting as player from now on. Resolve the outcome of player actions by simulating a dice roll for the player.'}
scenario = {'role': 'user', 'content': 'Describe a start for the following scenario: the player wakes up on a forest road with no memories, they are beside a caravan which has been destroyed, a trail leads from the wreckage into the forest whilst the road leads out of the forest.'}

startMessage = client.chat(model=model, messages=[
    rules,
    scenario,
])
print('GM:\n' + startMessage.message.content)

chatlogs = [rules, {'role': 'assistant', 'content': startMessage.message.content}]

while True:
    action = input('Describe the players\' actions: ')
    print('Player:\n' + action)
    chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history

    # Get response from model
    response = client.chat(model=model, messages=chatlogs)
    chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history

    print('GM:\n' + response.message.content)