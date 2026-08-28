from backend.services.llm import LLMClient
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


LLM = LLMClient()

REGISTRY = ToolRegistry() 
REGISTRY.register(CalculatorTool())
REGISTRY.register(WeatherTool())
REGISTRY.register(WebSearchTool())
REGISTRY.register(DateTimeTool())
REGISTRY.register(FileTool())
REGISTRY.register(LLMTool())
REGISTRY.register(CalendarTool())
REGISTRY.register(GmailTool())
REGISTRY.register(CodeWriterTool())

PLANNER = Planner(LLM , REGISTRY)