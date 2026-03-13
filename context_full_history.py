from rolls import rolls

def full_history(chatlogs, context_logs, memory, save, client, model, tokens):
    try:
        action = input('\nDescribe the player\'s actions: ')
        chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
        memory.append({'role': 'user',  'content': action})

        # Generate random rolls for model to use
        rolls_message = rolls()
        memory.append(rolls_message) # Add rolls message to models memory

        # Get response from model
        response = client.chat(model=model, messages=memory)

        # Save data
        context_logs.append(memory.copy()) # Append a copy of what the LLM had in memory at each prompt
        tokens += response.prompt_eval_count # Add tokens processed to token counter
        chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
        memory.append({'role': 'assistant',  'content': response.message.content})
        
        memory.remove(rolls_message) # Remove rolls message from memory

        print('\nGM:\n\n' + response.message.content)
        
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    return tokens