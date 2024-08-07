# Chatbot Interaction Script

This Python script is a proof-of-concept for testing a local Ollama server running on a remote Windows device. It allows you to interact with a chatbot model via an API, sending user prompts to the chatbot, receiving responses, and managing the conversation context to maintain a coherent dialogue. The script also logs the entire conversation to a text file.

## Features

- **Send Prompt**: Sends user input to the chatbot and receives responses.
- **Context Management**: Maintains and truncates the context to fit within a defined token limit.
- **Text Cleaning**: Cleans and formats the text to ensure proper readability.
- **Logging**: Logs the conversation to a text file for future reference.

## Requirements

- Python 3.x
- `requests` library

You can install the required library using pip:
```sh
pip install requests
```

## Script Breakdown

### Constants
- `MAX_TOKENS`: Defines the maximum number of tokens allowed in the context.

### Functions
- `send_prompt(prompt, context=[])`: Sends the user prompt along with the context to the chatbot API and returns the response.
- `clean_text(text)`: Cleans the input text by removing extra spaces and handling common formatting issues.
- `summarize_context(context, max_tokens=MAX_TOKENS)`: Summarizes the context to ensure it does not exceed the maximum token limit.

### Main Functionality
The `main()` function:
1. Initializes an empty context and a conversation log file.
2. Prompts the user for input in a loop until the user types 'exit'.
3. Sends the user input to the chatbot and receives the response.
4. Cleans and formats the response.
5. Updates the context with the user input and chatbot response.
6. Logs the conversation to a text file.

## Usage

To run the script, execute the following command:
```sh
python your_script_name.py
```

Replace `your_script_name.py` with the actual name of your Python script file.

### Example Interaction
```
Chat with your model. Type 'exit' to end the conversation.
You: Hello!
Model: Hi there! How can I assist you today?

You: What's the weather like today?
Model: I'm sorry, I don't have access to real-time weather information.

You: exit
```

The conversation will be logged in `conversation.txt` as follows:
```
You: Hello!
Model: Hi there! How can I assist you today?

You: What's the weather like today?
Model: I'm sorry, I don't have access to real-time weather information.
```

## Notes

- Ensure the API endpoint and model details are correctly configured in the script.
- The script assumes the API returns a list of JSON objects, each containing a message with the content.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
