import requests

# Simple function to chat with the API
def chat_with_bot(message, thread_id=None):
    url = "http://localhost:8000/chat"
    data = {"message": message}
    
    if user_id:
        data["user_id"] = user_id
    if thread_id:
        data["thread_id"] = thread_id
    
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Bot: {result['response']}")
        return result['thread_id']
    else:
        print(f"Error: {response.text}")
        return None

# Usage examples:
user_id, thread_id = chat_with_bot("What is the price of butter from Belgium?")
thread_id = chat_with_bot("Compare the average prices of milk and butter this year", thread_id)


'''
thread_id = chat_with_bot("What is the price of butter from Belgium?")
thread_id = chat_with_bot("Compare the average prices of milk and butter this year", thread_id)
thread_id = chat_with_bot("What about SMP from EEX EU?", thread_id)
thread_id = chat_with_bot("Show me the volatility of milk prices", thread_id)
'''