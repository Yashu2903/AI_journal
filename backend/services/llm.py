import ollama

def generate_reply(messages):
    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )
    return response["message"]["content"]
