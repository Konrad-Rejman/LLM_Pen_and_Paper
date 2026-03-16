from rolls import rolls

def full_history(chatlogs, context_logs, memory, client, model, tokens, save, backup):
    try:
        # If not loading from backup
        if memory[-1]['role'] == 'user': 
            action = input('\nDescribe the player\'s actions: ')
            chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history
            memory.append({'role': 'user',  'content': action})

            # Generate random rolls for model to use
            rolls_message = rolls()
            memory = [memory[0]] + [rolls_message] + memory[1:] # Add rolls message to models memory

        # Get response from model
        try:
            response = client.chat(model=model, messages=memory)
        except KeyboardInterrupt:
            save()
            quit()
        except Exception as e:
            print(e)
            backup(chatlogs, context_logs, memory, tokens)
            quit()
        
        # Save data
        context_logs.append([response.prompt_eval_count] + memory.copy()) # Append a copy of what the LLM had in memory at each prompt
        tokens += response.prompt_eval_count # Add tokens processed to token counter
        chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history
        memory.append({'role': 'assistant',  'content': response.message.content})
        
        memory.remove(rolls_message) # Remove rolls message from memory

        print('\nGM:\n\n' + response.message.content)
        
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    return tokens, memory