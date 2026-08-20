import uuid 
from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.llm import LLMClient
from backend.agent.agent import Agent
from backend.services.planner import Planner
from backend.tools.registry import ToolRegistry
from backend.tools.calculator import CalculatorTool
from backend.tools.date_time import DateTimeTool
from backend.tools.weather import WeatherTool
from backend.tools.web_search import WebSearchTool
from backend.tools.filetool import FileTool
from backend.tools.llm_tool import LLMTool
from backend.tools.calendar import CalendarTool
from backend.tools.gmail import GmailTool
from backend.services.code_writer import CodeWriterTool
from backend.memory.working_memory import WorkingMemory
from backend.memory.context_builder import ContextBuilder
import asyncio

app = FastAPI()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# GIVING USER AN IDENTITY 

llm = LLMClient()
working_memory = WorkingMemory(max_tokens = 2000)
context_builder = ContextBuilder(working_memory = working_memory , total_budget = 3000  )

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TOOL REGISTRATION 

registry = ToolRegistry() 
registry.register(CalculatorTool())
registry.register(WeatherTool())
registry.register(WebSearchTool())
registry.register(DateTimeTool())
registry.register(FileTool())
registry.register(LLMTool())
registry.register(CalendarTool())
registry.register(GmailTool())
registry.register(CodeWriterTool())

planner = Planner(llm , registry)


class ChatRequest(BaseModel):
    user_id : str
    session_id: str
    message: str
    

@app.post("/chat")
async def chat(query :str , user_id : str):
    #query = request.message 
    #user_id = request.user_id
    session_id = str(uuid.uuid4())
    agent = Agent(user_id , session_id , working_memory ,context_builder , planner , registry)
    reply = await agent.run(query)
    print("final reply is -> " ,reply )
    return {
        "reply": reply
    }


query = "hi , i am rajnil , i am about to get married , can you tell me about something rituals in chirtian marriages "
user_id = str(uuid.uuid4())
asyncio.run(chat(query , user_id))
