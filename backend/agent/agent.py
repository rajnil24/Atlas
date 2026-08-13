from backend.agent.execution_context import ExecutionContext
from backend.models.plan import Plan
from backend.models.plan import StepStatus
from backend.prompts.human_ans import HUMAN_ANS_PROMPT
from backend.services.llm import LLMClient 
from backend.scheduler.parallel_executor import ParallelExecutor
import asyncio 

class Agent:

    def __init__(
        self,
        planner,
        registry
    ):

        self.planner = planner
        self.registry = registry

    async def run(
        self,
        message: str,
        history: str,
    ): 
        plan : Plan = await self.planner.create_plan(message , history)
        print("message is ->" ,message)
        print(plan)
        llm = LLMClient()
        if len(plan.steps) == 0:
            reply = await llm.generate(message)
            return reply
        
        

        def serial_executor() :
            for step in plan.steps:
                        #print(step.step_id)
                        step.status = StepStatus.RUNNING
            
                        try:
                            print(step.tool_name)
                            tool = self.registry.get_tool(
                                step.tool_name
                            )
                            #print(step.tool_input)
                            tool_input = context.resolve(
                                step.tool_input
                            )
                            validated_input = tool.input_schema(
                                **tool_input
                            )
                            print(validated_input)
                            print(type(validated_input))
                            result = tool.run(
                                validated_input
                            )
                            #print(result)
                            if not result.success:
                                step.status = StepStatus.FAILED
                                step.error = result.error
                                print("returned from ageny.py line 57")
                                return {
                            
                                    "reply": result.error
            
                                }
            
                            step.status = StepStatus.SUCCESS
                            step.output = result.output
                            #print(step.output)
                            context.set_result(    
                                step.step_id,          
                                result.output,
                            )
            
                        except Exception as e:
            
                            step.status = StepStatus.FAILED
                            step.error = str(e)
                            print("returned form agent.py line 76")
                            return {
                                "reply": str(e)
                            }

        parallel_executor = ParallelExecutor(registry = self.registry , max_concurrency = 20 , step_timeout = 20.0) 
        context = await parallel_executor.execute_plan(plan)
        
        id = plan.steps[-1].step_id
        final_result = context.get_result(id)
        #print("final_result is ->" , final_result)

        for step in plan :
             attempt_history = step.attempt_history
             print("attempt history is ->" , attempt_history)

        async def nl_ans( plan_response) :
            prompt = HUMAN_ANS_PROMPT.format(plan = plan_response ,message = message 
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

        return reply
        
