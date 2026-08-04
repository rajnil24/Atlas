from backend.services.llm import LLMClient
from backend.tools.registry import ToolRegistry
from backend.prompts.prompt_planner import PLANNER_PROMPT
from backend.models.plan import Plan 
import json 

class Planner:

    def __init__(
        self,
        llm: LLMClient,
        registry: ToolRegistry,
    ):
        self.llm = llm
        self.registry = registry
      
    
    async def create_plan(
    self,
    message: str,
    history: str,
    ):
       tools = self.registry.get_tools_description()
       prompt = PLANNER_PROMPT.format(
    tools=tools,
    history=history,
    message=message
    )
       response = await self.llm.generate(prompt)
       
       response = response.replace("```json" , "")
       response = response.replace("```" , "")
       response = response.strip()
       print(response)
       dict_response = json.loads(response)
       list_response = Plan.model_validate(dict_response)
       list_response.plan_response = response
       return  list_response



