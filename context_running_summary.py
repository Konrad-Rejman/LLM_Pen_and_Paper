from rolls import rolls

def running_summary(chatlogs, rules, save, client, model, summary, tokens):
    try:
        action = input('\nDescribe the players\' actions: ')
        chatlogs.append({'role': 'user',  'content': action}) # Add Player input to chat history

        # Generate random rolls for model to use
        rolls = rolls()

        # Get response from model
        memory = [rules, rolls, {'role': 'system', 'content': 'This is an overview of the story so far: ' + summary}, {'role': 'user',  'content': action}]
        response = client.chat(model=model, messages=memory)
        tokens += response.prompt_eval_count # Add tokens processed to token counter
        chatlogs.append({'role': 'assistant',  'content': response.message.content}) # Add GM response to chat history

        print('\nGM:\n\n' + response.message.content)

        # Update the summary based on most recent context
        instructions = {'role': 'system', 'content': 'Update the following Summary without removing the capitalised heading: ' + summary}
        memory = [instructions, {'role': 'user',  'content': action}]
        new_summary = client.chat(model=model, messages=memory)
        tokens += new_summary.prompt_eval_count # Add tokens processed to token counter
        summary = new_summary.message.content
    
    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    return tokens, summary