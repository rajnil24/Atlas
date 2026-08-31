import os 
print("DATABASE_URL exists:", os.getenv("DATABASE_URL") is not None)
from fastapi import FastAPI
from backend.api.users import router as users_router
from backend.api.sessions import router as sessions_router
from backend.api.messages import router as messages_router
import asyncio

app = FastAPI(
    title = "Atlas API" ,
)
app.include_router(users_router)
app.include_router(sessions_router)
app.include_router(messages_router)

@app.get("/")

async def root():

    return {"message": "Atlas is running"}

    

@app.post("/chat")

async def main():

    query = "Hi, I am Rajnil. What is machine learning?"


    #reply = await chat(query, user_id)

    #print("final -> reply is", reply)

if __name__ == "__main__":
    asyncio.run(main())

