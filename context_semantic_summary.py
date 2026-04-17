from rolls import rolls
from rouge_score import rouge_scorer
import time, copy

def semantic_context(chatlogs, context_logs, memory, rules, client, model, hierarchical_summary, tokens, save, backup, n=3):
    try:
        old_chatlogs = copy.deepcopy(chatlogs)
        old_context_logs = copy.deepcopy(context_logs)
        old_memory = copy.deepcopy(memory)
        old_tokens = copy.deepcopy(tokens)

        rouge = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

        action = input('\nDescribe the players\' actions: ')
        chatlogs.append({'role': 'user',  'parts': [{'text': action}]}) # Add Player input to chat history

        # Generate random rolls for model to use
        rolls_message = rolls()
        memory = [rules, rolls_message, {'role': 'user', 'parts': [{'text': hierarchical_summary}]}] + memory[1:] + [{'role': 'user',  'parts': [{'text': action}]}] # Construct memory (rules, rolls, summary, last n interactions, user action)
        
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
        memory.append({'role': 'model',  'parts': [{'text': response.text}]}) # Add response to memory

        # Change memory to be ready for summary update
        memory.remove(rules) # Remove rules message
        memory.remove(rolls_message) # Remove rolls message from memory
        memory.remove({'role': 'user', 'parts': [{'text': hierarchical_summary}]}) # Remove summary message from memory

        # If memory is more than last n interactions (GM, Player) remove earliest interactions
        if len(memory) > 2*n:
            memory = memory[-2*n:] # memory = last n interactions

        # Update the summary based on most recent context, getting three potential updated summaries separated by a BREAK string
        instructions = {'role': 'user', 'parts': [{'text': 'Update the following Summary without removing its current headings or changing its current structure (OVERALL STORY, CURRENT QUEST, PLAYER STATUS). Give THREE examples of the updated summary each separated by a line containing ONLY the string BREAK. \n\nThis is the old summary: ' + hierarchical_summary}]}
        update = [instructions] + memory # Update according to the last n interactions
        try:
            time.sleep(5.1)
            hierarchical_summaries = client.models.generate_content(model=model, contents=update)
        except KeyboardInterrupt:
            save()
            quit()
        except Exception as e:
            try:
                time.sleep(1.1)
                hierarchical_summaries = client.models.generate_content(model=model, contents=update)
            except:
                try:
                    time.sleep(2.1)
                    hierarchical_summaries = client.models.generate_content(model=model, contents=update)
                except:
                    try:
                        time.sleep(4.1)
                        hierarchical_summaries = client.models.generate_content(model=model, contents=update)
                    except Exception as e:
                        print(e)
                        backup(old_chatlogs, old_context_logs, old_memory, old_tokens)
                        quit()
        tokens += hierarchical_summaries.usage_metadata.prompt_token_count # Add tokens processed to token counter
        hierarchical_summaries = hierarchical_summaries.text
        if hierarchical_summaries != None: # If summaries created correctly, else continue using old summary
            hierarchical_summaries = hierarchical_summaries.split('BREAK')

            # Scores dict for storing Rouge scores
            scores = {
                'rouge1': [],
                'rouge2': [],
                'rougeL': []
            }

            # Construct reference to compare summaries against
            last_n_interactions = ''
            for prompt in memory:
                last_n_interactions += (prompt['parts'][0]['text'] + '\n\n')
            reference_summary = hierarchical_summary + '\n\nLAST THREE INTERACTIONS:\n\n' + last_n_interactions

            # Get Rouge to score each summary
            for i in range(len(hierarchical_summaries)):
                r = rouge.score(hierarchical_summaries[i], reference_summary)
                # Add score values to scores list
                for x in r:
                    scores[x].append(r[x])

            # Select summary with highest overall Rouge score (f-measure) to be the new summary
            overall_scores = [sum(scores[r][i].fmeasure for r in scores) for i in range(len(hierarchical_summaries))]
            best = 0
            if len(overall_scores) > 1:
                for i in range(len(overall_scores)):
                    if overall_scores[i] > overall_scores[best]:
                        best = i
            hierarchical_summary = hierarchical_summaries[best]

        print('\nGM:\n\n' + response.text)

    except KeyboardInterrupt:
        save() # Save session data
        quit() # End program

    except Exception as e:
        print(e)
        backup(old_chatlogs, old_context_logs, old_memory, old_tokens)
        quit()

    return tokens, memory, hierarchical_summary