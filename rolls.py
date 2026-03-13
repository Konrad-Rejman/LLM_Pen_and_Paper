import random

def rolls():
    # Generate random rolls for model to use
    rolls = {'role': 'system', 'content': 'Use the following random rolls for this interaction if needed: '}
    roll_num = 5 # Number of random rolls to pass to model
    for i in range(roll_num): 
        r = random.randint(1, 20)
        rolls['content'] = rolls['content'] + str(r)
        if i < roll_num - 1:
            rolls['content'] = rolls['content'] + ', '

    return rolls # Return structured rolls message