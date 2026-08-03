from collections import deque 
from backend.models.plan import PlanStep , Plan
class schedule :

    def __init__(self) :
        self.graph : dict
        self.remaining_dependencies : dict 
        self.children : dict 

    def build_graph(self , plan : Plan) :
        for step in plan :
            id = step.step_id
            dependency = step.depends_on
            self.remaining_dependencies[id] = len(dependency)
            for child in dependency :
                self.children[id].append(child)

        que = deque() 
        for step_id , indegree in self.remaining_dependencies.items() :
            if indegree == 0 :  # depends on nothing
                que.push(step_id) 

        while que :


        
            


            

            



