from backend.agent.execution_context import ExecutionContext
from backend.models.plan import Plan
from backend.models.plan import StepStatus
from backend.prompts.human_ans import HUMAN_ANS_PROMPT
from backend.services.llm import LLMClient 
from backend.scheduler.parallel_executor import ParallelExecutor
from backend.memory.episode_store import EpisodicStore
from backend.memory.extractor import Extractor
import asyncio 

class Agent:

    def __init__(
        self,
        user_id,
        session_id,
        working_memory,
        context_builder,
        planner,
        registry
    ):
        self.user_id = user_id 
        self.session_id = session_id
        self.working_memory = working_memory
        self.context_builder = context_builder
        self.planner = planner
        self.registry = registry
        self.episodic_store = EpisodicStore()
        self.extractor = Extractor()

    async def run(
        self,
        query: str
    ):  
        build_context = await self.context_builder.build(user_id = self.user_id , session_id = self.session_id , query = query)
        plan : Plan = await self.planner.create_plan(query , build_context)
        print("build_context is ->" ,build_context)
        print(plan)
        llm = LLMClient()

        if len(plan.steps) == 0:
            reply = await llm.generate(query)
            return reply

        parallel_executor = ParallelExecutor(registry = self.registry , max_concurrency = 20 , step_timeout = 20.0) 
        context = await parallel_executor.execute_plan(plan)
        
        id = plan.steps[-1].step_id
        final_result = context.get_result(id)
        print("final_result is ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , final_result)

        async def nl_ans( plan_response) :
            prompt = HUMAN_ANS_PROMPT.format(plan = plan_response ,message = query 
                                             ,final_result=final_result)
            print("#################################")
            print("human nlp prompt is -> , " ,prompt)
            reply = await llm.generate(prompt)
            print("reply is ->" , reply)
            print("#################################")
            return reply
        
        plan_response = plan.plan_response
        #print(plan_response)
        reply = await nl_ans( plan_response)
        """
        print("------------------------------------")
        print(reply)
        print("------------------------------------")
        print("context results are ->" , context.results)
        """
        episodes = []

        episodes.append({
            "user_id" : self.user_id ,
            "session_id" : self.session_id ,
            "role" : "user" , 
            "content" : query ,
        })

        episodes.append({
            "user_id" : self.user_id ,
            "session_id" : self.session_id ,
            "role": "plan",
            "content": plan.model_dump_json(),
        })

        for step in plan.steps:
            episodes.append({
               "user_id" : self.user_id ,
               "session_id" : self.session_id ,
               "role": "tool",
               "content": step.tool_name,
               "meta": {
                  "step_id": step.step_id,
                  "tool_name": step.tool_name,
                  "tool_input": step.tool_input,
                  "status": step.status.value,
                  "output": step.output,
                  "error": step.error,
                  "retries": step.retries,
                  "depends_on": step.depends_on,
                },
            })

        episodes.append({
            "user_id" : self.user_id ,
            "session_id" : self.session_id ,
            "role" : "assistant" , 
            "content" : reply ,
        })

        await asyncio.to_thread(
            self.episodic_store.write_episodes_batch,
            episodes,
        )
        print("episodes are ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" , episodes)
        self.working_memory.add_turn(role = "user" , content = query)
        self.working_memory.add_turn(role = "assistant" , content = reply)
        print("line 119 agent.py")
        
        await self.extractor.run(user_id = self.user_id , session_id = self.session_id , episode_limit = 20)
        print("line 122 agent.py")
        return reply
        
