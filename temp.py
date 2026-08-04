from backend.services.llm import LLMClient
from backend.tools.registry import ToolRegistry
from backend.services.planner import Planner
from backend.tools.calculator import CalculatorTool
from backend.tools.date_time import DateTimeTool
from backend.tools.weather import WeatherTool
from backend.tools.web_search import WebSearchTool
from backend.tools.filetool import FileTool
from backend.tools.llm_tool import LLMTool
from backend.tools.calendar import CalendarTool
from backend.tools.gmail import GmailTool
from backend.services.code_writer import CodeWriterTool
from backend.agent.agent import Agent

llm = LLMClient() 
registry = ToolRegistry()
registry.register(CalculatorTool())
registry.register(DateTimeTool())
registry.register(WeatherTool())
registry.register(WebSearchTool())
registry.register(FileTool())
registry.register(LLMTool())
registry.register(CalendarTool())
registry.register(GmailTool())
registry.register(CodeWriterTool())

planner = Planner(llm , registry)
history = ""

agent = Agent(planner , registry )

op = agent.run("  " , history )