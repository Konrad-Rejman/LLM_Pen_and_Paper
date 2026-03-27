import random

def rolls():
    # Generate random rolls for model to use
    rolls = {'role': 'user', 'parts': [{'text': 'Use the following random rolls for this interaction if needed: '}]}
    roll_num = 5 # Number of random rolls to pass to model
    for i in range(roll_num): 
        r = random.randint(1, 20)
        rolls['parts'][0]['text'] = rolls['parts'][0]['text'] + str(r)
        if i < roll_num - 1:
            rolls['parts'][0]['text'] = rolls['parts'][0]['text'] + ', '

    return rolls # Return structured rolls message