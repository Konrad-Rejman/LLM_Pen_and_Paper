from rolls import rolls

def full_history(chatlogs, context_logs, memory, client, model, tokens, save, backup):
    try:
        action = input('\nDescribe the player\'s actions: ')
        chatlogs.append({'role': 'user',  'parts': [{'text': action}]}) # Add Player input to chat history
        memory.append({'role': 'user',  'parts': [{'text': action}]})

        # Generate random rolls for model to use
        rolls_message = rolls()
        memory = [memory[0]] + [rolls_message] + memory[1:] # Add rolls message to models memory

        # Get response from model
        try:
            response = client.models.generate_content(model=model, contents=memory)
        except KeyboardInterrupt:
            save()
            quit()
        except Exception as e:
            print(e)
            backup(chatlogs, context_logs, memory, tokens)
            quit()
        
        # Save data
        context_logs.append([response.usage_metadata.prompt_token_count] + memory.copy()) # Append a copy of what the LLM had in memory at each prompt
        tokens += response.usage_metadata.prompt_token_count # Add tokens processed to token counter
        chatlogs.append({'role': 'model',  'parts': [{'text': response.text}]}) # Add GM response to chat history
        memory.append({'role': 'model',  'parts': [{'text': response.text}]})
        
        memory.remove(rolls_message) # Remove rolls message from memory

        print('\nGM:\n\n' + response.text)
        
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program
    
    except Exception as e:
        print(e)
        backup(chatlogs, context_logs, memory, tokens)
        quit()

    return tokens, memory