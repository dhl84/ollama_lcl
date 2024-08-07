import requests
import json
import re

def send_prompt(prompt, context=[]):
    url = "http://192.168.1.125:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "llama3.1:latest",
        "messages": context + [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    responses = response.content.decode().strip().split('\n')
    result = [json.loads(r) for r in responses if r.strip()]  # Ensure non-empty lines
    return result

def clean_text(text):
    # Remove extra spaces and handle common formatting issues
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'\s([?.!",\'])', r'\1', text)  # Remove spaces before punctuation
    text = re.sub(r' (?=\n)', '', text)  # Remove space before newline
    text = re.sub(r'\n\s+', '\n', text)  # Remove space after newline
    return text.strip()

def main():
    context = []
    print("Chat with your model. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

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
        context.append({"role": "user", "content": user_input})
        print(f"Model: {cleaned_response}\n")
        # print(f"Original JSON: {json.dumps(original_json, indent=2)}")

if __name__ == "__main__":
    main()
