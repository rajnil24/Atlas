from backend.agent.execution_context import ExecutionContext
from backend.models.plan import Plan
from backend.models.plan import StepStatus
from backend.prompts.human_ans import HUMAN_ANS_PROMPT
from backend.services.llm import LLMClient 
from backend.scheduler.parallel_executor import ParallelExecutor
from backend.memory.episode_store import EpisodicStore
from backend.memory.extractor import Extractor
import asyncio 
import time 

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
        t = time.perf_counter()
        build_context = await self.context_builder.build(user_id = self.user_id , session_id = self.session_id , query = query)
        print(f"$$$$$$$$$$[TIMING]$$$$$$$$$$$$$$$$$$ ContextBuilder: {time.perf_counter() - t:.2f}s")
        t = time.perf_counter()
        plan : Plan = await self.planner.create_plan(query , build_context)
        print(f"$$$$$$$$$$[TIMING]$$$$$$$$$$$$$$$$$$ Planning: {time.perf_counter() - t:.2f}s")
        print(plan)
        
        llm = LLMClient()

        plan_required = True
        if len(plan.steps) == 0:
            #reply = await llm.generate(query)
            plan_required = False
            #return reply
        
        final_result = ""
        if plan_required :
            
            parallel_executor = ParallelExecutor(registry = self.registry , max_concurrency = 20 , step_timeout = 20.0) 

            t = time.perf_counter()
            context = await parallel_executor.execute_plan(plan)
            print(f"$$$$$$$$$$[TIMING]$$$$$$$$$$$$$$$$$$ PLAN EXECUTION: {time.perf_counter() - t:.2f}s")
            id = plan.steps[-1].step_id
            final_result = context.get_result(id)
            
        #print("final_result is ->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" , final_result)
        t = time.perf_counter()

        async def nl_ans( plan_response) :
            prompt = HUMAN_ANS_PROMPT.format(plan = plan_response ,message = query 
                                             ,final_result=final_result)
            
            reply = await llm.generate(prompt)
            
            return reply
        
        plan_response = plan.plan_response
       
        reply = await nl_ans( plan_response)

        print(f"$$$$$$$$$$[TIMING]$$$$$$$$$$$$$$$$$$ Final_ans_by_llm: {time.perf_counter() - t:.2f}s")

        

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

        t = time.perf_counter()

        print(
        f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$[EPISODE] [{self.session_id}] Before to_thread: "
        f"{time.perf_counter():.4f}"
)
        
        await asyncio.to_thread(
            self.episodic_store.write_episodes_batch,
            episodes,
            self.session_id,
        )
        
        print(

    f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$[EPISODE][{self.session_id}]  After to_thread: "

    f"{time.perf_counter():.4f}"

)

        print(
    f"$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$[EPISODE] Total await time: "
    f"{time.perf_counter() - t:.2f}s"
)

        t = time.perf_counter()
    
        self.working_memory.add_turn(role = "user" , content = query)

        self.working_memory.add_turn(role = "assistant" , content = reply)

        print(f"[TIMING] Working_Memory DB write: {time.perf_counter() - t:.2f}s")
        
        t = time.perf_counter()

        await self.extractor.run(user_id = self.user_id , session_id = self.session_id , episode_limit = 20)

        print(f"[TIMING] Extractor DB write: {time.perf_counter() - t:.2f}s")

        
        return reply
        
