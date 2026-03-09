import ollama, os, random
import pandas as pd
from dotenv import load_dotenv
from context_full_history import full_history
from context_n_latest import n_latest
from context_running_summary import running_summary
from context_hierarchical_context_injection import hierarchical_context

load_dotenv()

client = ollama.Client(host=os.getenv('HOSTURL'))

# Models: ['qwen3:32b', 'gemma3:12b', 'deepseek-r1:32b', 'gpt-oss:120b', 'llama3.1:8b', 'llama3.2:latest', 'gpt-oss:latest']
model = 'gpt-oss:120b'

# Game start
print('Press ctrl + c to exit.')
print('The LLM will act as the Game Master (GM), play along by inputing your characters actions each turn and the LLM will respond with the outcome setting up the next turn.')
print('Generating...')

# Get user identifier
user = input('Enter your username (please use the same username for each session): ')

# Choose a context method the user hasn't used yet randomly, else choose a random method
context_methods = ['Full_Context', 'N_Latest', 'Running_Summary', 'Hierarchical_Summary'] # List of implemented methods
random.shuffle(context_methods) # Randomise order of methods

# Check data file for users previous sessions
df = pd.read_csv('data.csv', index_col=0)
df = df[df['User'] == user]

# Choose a method the user hasn't seen yet, if possible
method = None

seen = set(v for i, v in df['Context Method'].items()) # Get set of context methods the user has seen already

for m in context_methods:
    if m not in seen: # If user has not seen context method, use that method
        method = m
        break

if not method: # If user has used every context method at least once, choose a random method
    method = random.choice(context_methods)

# Model setup
rules = {'role': 'system', 'content': 'RULES: Act as the GameMaster for the following pen and paper game, with the user acting as player from now on. Resolve the outcome of player actions by simulating a dice roll for the player, a list of random rolls will be provided for you to use. Provide your response in clear plaintext, without any markdown or special characters.'}
scenario = {'role': 'user', 'content': 'Describe a start for the following scenario: the player wakes up on a forest road with no memories, they are beside a caravan which has been destroyed, a trail leads from the wreckage into the forest surrounding them. Set up future quests and recurring characters.'}

startMessage = client.chat(model=model, messages=[
    rules,
    scenario,
])
print('GM:\n' + startMessage.message.content)

chatlogs = [{'role': 'assistant', 'content': startMessage.message.content}] # Full chat history
memory = [{'role': 'assistant', 'content': startMessage.message.content}] # Model context

# Run on exit
def save():
    # Save session info
    file_number = 0
    for f in os.listdir('sessions'):
        session_number = int(f.split('_')[0])
        if session_number > file_number: # Last session number
            file_number = session_number 

    # Construct file name
    file_name = str(file_number+1) + '_' + method + '_' + user
    file_path = os.path.join('sessions', file_name + '.txt')

    # Write a file containing the session chatlogs
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in chatlogs:
            if line['role'] == 'assistant':
                file.write('GM:\n' + line['content'] + '\n\n')
            elif line['role'] == 'user':
                file.write('PLAYER:\n' + line['content'] + '\n\n')

    # Get feedback
    valid_numbers = set(['1', '2', '3', '4', '5', '6', '7'])

    def feedback():
        print('On a scale of 1 - 7, how would you rate the completed session on the following:\n')
        global consistency, adherence, creativity, enjoyment
        consistency = input('The GMs ability to maintain a consistent narrative: ')
        adherence = input('The GMs ability to follow established rules: ')
        creativity = input('The GMs creativity in storytelling: ')
        enjoyment = input('Your overall enjoyment of the game session: ')

        # If any of the values entered are not valid numbers
        if consistency not in valid_numbers or adherence not in valid_numbers or creativity not in valid_numbers or enjoyment not in valid_numbers:
            print('\nOne of the values you entered was not between 0 and 10, please try again.')
            feedback()

    feedback()

    session_data = {
        'Session': [file_name], 
        'User': [user],
        'Context Method': [method],
        'Consistency (1-7)': [consistency], 
        'Rule Adherence (1-7)': [adherence], 
        'Creativity (1-7)': [creativity], 
        'Enjoyment (1-7)': [enjoyment], 
        'Tokens': [0], 
        'Playtime': [0]
    }
    new_row = pd.DataFrame(session_data)

    # Add the session feedback to the data csv
    df = pd.read_csv('data.csv', index_col=0)
    df = pd.concat([df, new_row])
    df.to_csv('data.csv')

# Summaries of overall story, these are updated in the Running_Summary and Hierarchical_Summary context methods
summary = 'STORY SUMMARY: The player has woken up on a forest road with no memories and nothing but the clothes on their back, they are beside a caravan which has been destroyed, a trail leads from the wreckage into the forest surrounding them. The player must find civilization and uncover clues as to their identity along the way, they should also be given the chance to help the people they encounter by fighting monsters.'
hierarchical_summary = 'OVERALL STORY: The player must find civilization and uncover clues as to their identity along the way, they should also be given the chance to help the people they encounter by fighting monsters.\n\nCURRENT QUEST: The player is beside a caravan which has been destroyed, a trail leads from the wreckage into the forest surrounding them. The player must find a way out of the forest.\n\nPLAYER STATUS: The player has woken up with no memories and nothing but the clothes on their back.'

# Core loop, prompting the Model to continue with the story until the player exits using Ctrl + C
while True:
    if method == 'Full_Context':
        full_history(chatlogs, [rules] + [{'role': 'system', 'content': summary}] + memory, save, client, model)
    elif method == 'N_Latest':
        n_latest(chatlogs, [rules] + [{'role': 'system', 'content': summary}] + memory, save, client, model)
    elif method == 'Running_Summary':
        summary = running_summary(chatlogs, rules, save, client, model, summary)
    elif method == 'Hierarchical_Summary':
        hierarchical_summary = hierarchical_context(chatlogs, rules, save, client, model, hierarchical_summary)