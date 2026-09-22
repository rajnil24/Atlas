from fastapi import FastAPI
from backend.api.users import router as users_router
from backend.api.sessions import router as sessions_router
from backend.api.messages import router as messages_router
from backend.api.auth import router as auth_router
from backend.api.chat import router as chat_router
from fastapi import Depends
from backend.dependencies.auth import get_current_user
from fastapi.middleware.cors import CORSMiddleware
 

app = FastAPI(
    title = "Atlas API" ,
)
app.include_router(users_router)
app.include_router(sessions_router)
app.include_router(messages_router)
app.include_router(auth_router)
app.include_router(chat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")

async def root():
    return {"message": "Atlas is running"}

    

