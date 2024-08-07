import sys
import subprocess
import psutil
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

def extract_relevant_info(text, start_marker, end_marker):
    start_index = text.find(start_marker)
    end_index = text.find(end_marker, start_index)
    if start_index != -1 and end_index != -1:
        return text[start_index:end_index + len(end_marker)]
    return ""

def monitor_resources(context):
    # Monitor CPU and RAM usage on local machine
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    
    # Use ollama's built-in functions to get resource usage from the remote server
    try:
        # List running models
        models_ps = subprocess.run(["ollama", "ps"], capture_output=True, text=True)
        models_info = extract_relevant_info(models_ps.stdout, "Running Models:", "NAME   ID      SIZE    PROCESSOR       UNTIL")
        print(models_info)
        
        # Show model information (commented out to prevent printing)
        # model_info = subprocess.run(["ollama", "show", "llama3.1"], capture_output=True, text=True)
        # print("Model Information:\n", model_info.stdout)
    except Exception as e:
        print(f"Failed to fetch resource usage data: {e}")

    # Monitor context size
    context_text = " ".join([msg["content"] for msg in context])
    context_size = len(context_text.split())

    print(f"CPU Usage: {cpu_usage}%")
    print(f"RAM Usage: {ram_usage}%")
    print(f"Context Size: {context_size} words")

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
        original_json = []
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
                    context.append({"role": "assistant", "content": message.strip()})

                original_json.append(res)
        
        # Join the full response parts with a space and clean it
        cleaned_response = clean_text(' '.join(full_response))
        print(f"Model: {cleaned_response}\n")

        approval = input("Do you approve this response? (y/n): ").strip().lower()
        if approval == "y":
            context.append({"role": "user", "content": user_input})
            context.append({"role": "assistant", "content": cleaned_response})
        else:
            print("Response rejected. Please enter a new prompt.")

        # print(f"Original JSON: {json.dumps(original_json, indent=2)}")
        
        # Monitor and display resources
        monitor_resources(context)

if __name__ == "__main__":
    main()
