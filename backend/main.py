import uuid 
from fastapi import FastAPI
from backend.api.users import router as users_router
from backend.api.sessions import router as sessions_router
from backend.api.messages import router as messages_router

import asyncio
from pydantic import BaseModel

app = FastAPI(
    title = "Atlas API" ,
)
app.include_router(users_router)
app.include_router(sessions_router)
app.include_router(messages_router)

@app.get("/")

async def root():

    return {"message": "Atlas is running"}

class ChatRequest(BaseModel):
    user_id : str
    session_id: str
    message: str
    

@app.post("/chat")

async def main():

    query = "Hi, I am Rajnil. What is machine learning?"

    user_id = str(uuid.uuid4())

    reply = await chat(query, user_id)

    print("final -> reply is", reply)

if __name__ == "__main__":
    asyncio.run(main())

