from rolls import rolls
import time, copy

def running_summary(chatlogs, context_logs, memory, rules, client, model, summary, tokens, save, backup):
    try:
        old_chatlogs = copy.deepcopy(chatlogs)
        old_context_logs = copy.deepcopy(context_logs)
        old_memory = copy.deepcopy(memory)
        old_tokens = copy.deepcopy(tokens)

        action = input('\nDescribe the players\' actions: ')
        chatlogs.append({'role': 'user',  'parts': [{'text': action}]}) # Add Player input to chat history

        # Generate random rolls for model to use
        rolls_message = rolls()

        memory = [rules, rolls_message, {'role': 'user', 'parts': [{'text': summary}]}, {'role': 'user',  'parts': [{'text': action}]}]
        
        # Get response from model
        try:
            response = client.models.generate_content(model=model, contents=memory)
        except KeyboardInterrupt:
            save()
            quit()
        except Exception as e:
            try:
                time.sleep(1.1)
                response = client.models.generate_content(model=model, contents=memory)
            except:
                try:
                    time.sleep(2.1)
                    response = client.models.generate_content(model=model, contents=memory)
                except:
                    try:
                        time.sleep(4.1)
                        response = client.models.generate_content(model=model, contents=memory)
                    except Exception as e:
                        print(e)
                        backup(old_chatlogs, old_context_logs, old_memory, old_tokens)
                        quit()
        # Save data
        context_logs.append([response.usage_metadata.prompt_token_count] + memory.copy()) # Append a copy of what the LLM had in memory at each prompt
        tokens += response.usage_metadata.prompt_token_count # Add tokens processed to token counter
        chatlogs.append({'role': 'model',  'parts': [{'text': response.text}]}) # Add GM response to chat history

        print('\nGM:\n\n' + response.text)

        # Update the summary based on most recent context
        instructions = {'role': 'user', 'parts': [{'text': 'Update the following Summary without removing the capitalised heading ' + summary}]}
        update = [instructions, {'role': 'user',  'parts': [{'text': action}]}]
        try:
            new_summary = client.models.generate_content(model=model, contents=update)
        except KeyboardInterrupt:
            save()
            quit()
        except Exception as e:
            try:
                time.sleep(1.1)
                new_summary = client.models.generate_content(model=model, contents=update)
            except:
                try:
                    time.sleep(2.1)
                    new_summary = client.models.generate_content(model=model, contents=update)
                except:
                    try:
                        time.sleep(4.1)
                        new_summary = client.models.generate_content(model=model, contents=update)
                    except Exception as e:
                        print(e)
                        backup(old_chatlogs, old_context_logs, old_memory, old_tokens)
                        quit()
        tokens += new_summary.usage_metadata.prompt_token_count # Add tokens processed to token counter
        summary = new_summary.text
    
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program
    
    except Exception as e:
        print(e)
        backup(old_chatlogs, old_context_logs, old_memory, old_tokens)
        quit()

    return tokens, memory, summary