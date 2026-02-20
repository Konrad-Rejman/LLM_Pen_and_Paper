import ollama, os, atexit, re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

client = ollama.Client(host=os.getenv('HOSTURL'))

# Models: ['qwen3:32b', 'gemma3:12b', 'deepseek-r1:32b', 'gpt-oss:120b', 'llama3.1:8b', 'llama3.2:latest', 'gpt-oss:latest']
model = 'gpt-oss:120b'

# Game start
print('Press ctrl + c to exit.')
print('The LLM will act as the Game Master (GM), play along by inputing your characters actions each turn and the LLM will respond with the outcome setting up the next turn.')
print('Generating...')

rules = {'role': 'system', 'content': 'Act as the GameMaster for the following pen and paper game, with the user acting as player from now on. Resolve the outcome of player actions by simulating a dice roll for the player, do not ask them to perform the roll. Keep your responses brief. Use standard characters.'}
scenario = {'role': 'user', 'content': 'Describe a start for the following scenario: the player wakes up on a forest road with no memories, they are beside a caravan which has been destroyed, a trail leads from the wreckage into the forest whilst the road leads out of the forest.'}

startMessage = client.chat(model=model, messages=[
    rules,
    scenario,
])
print('GM:\n' + startMessage.message.content)

chatlogs = [{'role': 'assistant', 'content': startMessage.message.content}] # Full chat history
memory = [rules, {'role': 'assistant', 'content': startMessage.message.content}] # Model context

# Run on exit
def exit():
    # Save session info
    file_number = 0
    for f in os.listdir('sessions'):
        if int(re.sub(r'[^0-9]', '', f)) > file_number:
            file_number = int(re.sub(r'[^0-9]', '', f)) # Last session number

    # Construct file name
    file_name = 'session_' + str(file_number+1)
    file_path = os.path.join('sessions', file_name + '.txt')

    # Write a file containing the session chatlogs
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in chatlogs:
            if line['role'] == 'assistant':
                file.write('GM:\n' + line['content'] + '\n\n')
            elif line['role'] == 'user':
                file.write('PLAYER:\n' + line['content'] + '\n\n')

    # Get feedback
    print('On a scale of 0 - 10, how would you rate the completed session on the following:\n')
    consistency = input('The GMs ability to maintain a consistent narrative: ')
    adherence = input('The GMs ability to follow established rules: ')
    creativity = input('The GMs creativity in storytelling: ')
    enjoyment = input('Your overall enjoyment of the game session: ')

    session_data = {
        'Session': [file_name], 
        'Consistency (0-10)': [consistency], 
        'Rule Adherence (0-10)': [adherence], 
        'Creativity (0-10)': [creativity], 
        'Enjoyment (0-10)': [enjoyment], 
        'Tokens': [0], 
        'Playtime': [0]
    }
    new_row = pd.DataFrame(session_data)

    # Add the session feedback to the data csv
    df = pd.read_csv('data.csv', index_col=0)
    df = pd.concat([df, new_row])
    df.to_csv('data.csv')

atexit.register(exit)

while True:
    action = input('Describe the players\' actions: ')
    chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
    memory.append({'role': 'user',  'content': action})

    # Get response from model
    response = client.chat(model=model, messages=memory)
    chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
    memory.append({'role': 'assistant',  'content': response.message.content})

    print('GM:\n' + response.message.content)