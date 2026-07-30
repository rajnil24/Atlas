from collections import deque 

class ChatMemory :
    def __init__(self , max_history : int = 20) :
        self.conversations = {} 
        self.max_history = max_history

    def add_message(self , content : str , session_id : str , role : str) :
        if  session_id not in self.conversations :
            self.conversations[session_id] = deque(maxlen = self.max_history)

        self.conversations[session_id].append({
            "role" : role,
            "content" : content
        })
    
    def get_message(self , session_id : str) : 
        if session_id not in self.conversations :
            return []
        return list(self.conversations[session_id])
    
    def clear(self, session_id: str):
        if session_id in self.conversations:
            del self.conversations[session_id]



