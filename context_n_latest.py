from rolls import rolls

def n_latest(chatlogs, context_logs, memory, save, client, model, tokens, n=5):
    try:
        action = input('\nDescribe the player\'s actions: ')
        chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
        memory.append({'role': 'user',  'content': action})

        # Generate random rolls for model to use
        rolls_message = rolls()
        memory = [memory[0]] + [rolls_message] + memory[1:] # Add rolls message to models memory

        # Get response from model
        response = client.chat(model=model, messages=memory)

        # Save data
        context_logs.append(memory.copy()) # Append a copy of what the LLM had in memory at each prompt
        tokens += response.prompt_eval_count # Add tokens processed to token counter
        chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
        memory.append({'role': 'assistant',  'content': response.message.content})

        memory.remove(rolls_message) # Remove rolls message from memory

        print('\nGM:\n\n' + response.message.content)

        # If memory is more than last n interactions (GM, Player) excluding rules and summary, remove earliest interactions
        if len(memory[2:]) > 2*n:
            memory = [memory[0]] + memory[-2*n:] # memory = rules + last n interactions
        
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program
    
    return tokens, memory