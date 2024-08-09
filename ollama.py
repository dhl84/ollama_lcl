import sys
import re
import requests
import json
import argparse

MAX_TOKENS = 4000  # Define a limit for the context window

def send_prompt(prompt, context=[]):
    url = "http://192.168.1.125:11434/api/chat"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "llama3.1:latest",
        "messages": context + [{"role": "user", "content": prompt}]
    }

    # print(f"Sending payload (first 200 chars): {str(payload)[:200]}")
    
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

def main(document_path=None):
    context = []
    conversation_file = "conversation.txt"
    document_summaries = []
    
    if document_path:
        try:
            with open(document_path, 'r', encoding='utf-8') as file:
                document_content = file.read()
            print(f"Document loaded: {document_path}")
            print(f"Document length: {len(document_content)} characters")
            
            chunk_size = 8000
            chunks = [document_content[i:i+chunk_size] for i in range(0, len(document_content), chunk_size)]
            
            print(f"Document split into {len(chunks)} chunks of {chunk_size} characters each.")
            
            for i, chunk in enumerate(chunks):
                print(f"\nAnalyzing chunk {i+1}/{len(chunks)}")
                test_prompt = f"Here's a part of a document to analyze (part {i+1}/{len(chunks)}):\n\n{chunk}\n\nPlease summarize the key points of this part of the document in 2-3 sentences."
                results = send_prompt(test_prompt, [])  # Empty context for each chunk
                
                full_response = []
                for res in results:
                    if 'message' in res:
                        full_response.append(res['message']['content'])
                
                cleaned_response = clean_text(' '.join(full_response))
                print(f"Summary: {cleaned_response}\n")
                document_summaries.append(cleaned_response)
            
            # Add a condensed version of all summaries to the context
            context.append({"role": "system", "content": "You have analyzed a document in multiple parts. Here are the key points from each part: " + " ".join(document_summaries)})
            
            print("\nDocument analysis complete. You can now ask questions about the document.")
            
        except FileNotFoundError:
            print(f"Error: The file {document_path} was not found.")
            return
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return

    print("Chat with your model. Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Include the document context in each prompt
        full_prompt = f"Based on the document analysis provided earlier, please answer the following question: {user_input}"
        results = send_prompt(full_prompt, context)
        
        full_response = []
        for res in results:
            if 'message' in res:
                full_response.append(res['message']['content'])
        
        cleaned_response = clean_text(' '.join(full_response))
        print(f"Model: {cleaned_response}\n")

        # Log the conversation to the file
        with open(conversation_file, "a", encoding="utf-8") as log_file:
            log_file.write(f"You: {user_input}\n")
            log_file.write(f"Model: {cleaned_response}\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with an Ollama model and optionally analyze a text document.")
    parser.add_argument("--document", type=str, help="Path to the text document to analyze", default=None)
    args = parser.parse_args()
    
    main(args.document)