import random

def running_summary(chatlogs, rules, memory, save, client, model, summary=False):
    try:
        action = input('\nDescribe the players\' actions: ')
        chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
        memory.append({'role': 'user',  'content': action})
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    # Generate random rolls for model to use
    rolls = {'role': 'system', 'content': 'Use the following random rolls for this interaction as needed: '}
    roll_num = 5 # Number of random rolls to pass to model
    for i in range(roll_num): 
        r = random.randint(1, 20)
        rolls['content'] = rolls['content'] + str(r)
        if i < roll_num - 1:
            rolls['content'] = rolls['content'] + ', '

    # Get response from model
    memory.append(rules) # Add rules to memory
    memory.append(rolls) # Add rolls to memory
    response = client.chat(model=model, messages=memory)
    chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
    memory.append({'role': 'assistant',  'content': response.message.content})
    memory.remove(rules) # Remove rules message from memory
    memory.remove(rolls) # Remove rolls message from memory

    print('GM:\n' + response.message.content)

    # Update the summary based on most recent context
    instructions = {'role': 'system', 'content': 'Update the following Summary: ' + summary}
    memory = [instructions, {'role': 'user',  'content': action}]
    new_summary = client.chat(model=model, messages=memory).message.content
    summary = new_summary
    memory = [{'role': 'system', 'content': 'Summary of the story so far: ' + summary}]

    return summary