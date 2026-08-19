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
    query : str,
    build_context,
    ):
       tools = self.registry.get_tools_description()
       known_facts = build_context.get("known_facts" , "")
       conversation_history = build_context.get("conversation_history" , "")
       prompt = PLANNER_PROMPT.format(
    tools=tools,
    conversation_history = conversation_history ,
    known_facts=known_facts,
    query=query
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



