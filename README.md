# LLM Context Retention and Narrative Consistency Project Repo

### By Konrad Rejmanowski

## Setup:

### Installation:

You will need the following packages installed in order to run the program:

1. Python
2. ollama
2. pandas
3. dotenv

You can check for dependencies in the requirements.txt file.

### Additional Files / Directories:

You will need to initialise the following correctly:

- A .env file with your 'HOSTURL' variable declared (this is a link to the host of your OLLAMA model).
- A data.csv file with the headings ',Session,User,Context Method,Consistency (1-7),Rule Adherence (1-7),Creativity (1-7),Enjoyment (1-7),Tokens,Playtime (s)' for data on the sessions and feedback to be collected.
- A 'sessions' folder in the root directory for session transcripts to be saved.

### Running Program:

To run the program, follow all previous instructions and (ensuring you are in the correct root directory in terminal) run the command 'python main.py'. 

The program should run correctly from there, initialising the model and starting the gameplay loop. To exit the program, press ctrl + c and input the feedback on the session.