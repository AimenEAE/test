from openai import OpenAI
import os
# Replace with your actual OpenAI API key

client =OpenAI(api_key= os.getenv("OPENAI_API_KEY"))

def get_chatbot_response(user_input, system_message_path, conversation_history):
    system_message = open_file(system_message_path)
    messages = [{"role": "system", "content": system_message}] + conversation_history + [{"role": "user", "content": user_input}]

    streamed_completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return streamed_completion.choices[0].message.content

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()
