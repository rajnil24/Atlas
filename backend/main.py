from fastapi import FastAPI
from pydantic import BaseModel
from backend.services.llm import LLMClient
from backend.services.chat_memory import ChatMemory
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

app = FastAPI()
llm = LLMClient()
memory = ChatMemory() 

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
agent = Agent(planner , registry)

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    query = request.message 
    session_id = request.session_id
    history = memory.get_message(session_id)
    memory.add_message(
        query ,
        session_id ,
        role = "user"
    )
    reply = agent.run(query , history)
    memory.add_message(
        content =  reply ,
        session_id = request.session_id ,
        role = "assistant"
    )
 
    return {
        "reply": reply
    }