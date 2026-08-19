import requests
import uuid

url = "http://127.0.0.1:8000/chat"
user_id = str(uuid.uuid4())
print("\n")
print("============================Session Started==========================")
print("\n")
while True:
    message = input("You: ")
    if message == "exit" or message == "stop":
        break 
    response = requests.post(
        url,
        json={
            "message": message , 
            "user_id":user_id
        }
    )
    
    print("\n")
    print(response.json()["reply"])
    print("\n")
    print("="*90)