import sys
import re
import requests
import json

MAX_TOKENS = 1024  # Define a limit for the context window

def send_prompt(prompt, context=[]):
    url = "http://192.168.1.125:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.1:latest",
        "messages": context + [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        responses = response.content.decode().strip().split('\n')
        result = [json.loads(r) for r in responses if r.strip()]  # Ensure non-empty lines
        return result
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

def clean_text(text):
    # Remove extra spaces and handle common formatting issues
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'\s([?.!",\'])', r'\1', text)  # Remove spaces before punctuation
    return text.strip()

def summarize_context(context, max_tokens=MAX_TOKENS):
    context_text = " ".join([msg["content"] for msg in context])
    context_words = context_text.split()

    if len(context_words) > max_tokens:
        # Truncate older parts of the context to fit within max_tokens
        truncated_context = context_words[-max_tokens:]
        truncated_text = " ".join(truncated_context)
        # Create a new context with truncated text
        new_context = [{"role": "assistant", "content": truncated_text}]
        return new_context
    return context

def main():
    context = []
    conversation_file = "conversation.txt"
    print("Chat with your model. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Summarize context if it exceeds the maximum token limit
        context = summarize_context(context)

        results = send_prompt(user_input, context)
        full_response = []
        partial_word = ""

        for res in results:
            if 'message' in res:
                message = res['message']['content']
                # Check if the previous part ended mid-word
                if partial_word:
                    message = partial_word + message
                    partial_word = ""
                # Check if the current message ends mid-word
                if re.match(r'.*\w$', message):
                    partial_word = message
                else:
                    full_response.append(message.strip())
        
        # Join the full response parts with a space and clean it
        cleaned_response = clean_text(' '.join(full_response))
        print(f"Model: {cleaned_response}\n")

        # Update context with user input and model response
        context.append({"role": "user", "content": user_input})
        context.append({"role": "assistant", "content": cleaned_response})
        
        # Log the conversation to the file
        with open(conversation_file, "a", encoding="utf-8") as log_file:
            log_file.write(f"You: {user_input}\n")
            log_file.write(f"Model: {cleaned_response}\n\n")

if __name__ == "__main__":
    main()