import random

def full_history(chatlogs, memory, save, client, model):
    try:
        action = input('Describe the players\' actions: ')
        chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
        memory.append({'role': 'user',  'content': action})
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    # Generate random rolls for model to use
    rolls = {'role': 'system', 'content': 'Use the following random rolls for this interaction if needed: '}
    roll_num = 5 # Number of random rolls to pass to model
    for i in range(roll_num): 
        r = random.randint(1, 20)
        rolls['content'] = rolls['content'] + str(r)
        if i < roll_num - 1:
            rolls['content'] = rolls['content'] + ', '
    memory.append(rolls) # Add rolls message to models memory

    # Get response from model
    response = client.chat(model=model, messages=memory)
    chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
    memory.append({'role': 'assistant',  'content': response.message.content})
    memory.remove(rolls) # Remove rolls message from memory

    print('GM:\n' + response.message.content)