from pydantic import BaseModel 
from backend.config import settings 
from backend.tools.base_tools import BaseTool , ToolResult 
from tavily import TavilyClient

class WebSearchInput(BaseModel) :
    query : str 

class WebSearchTool(BaseTool) :
    tool_name = "websearch"
    tool_description = "Input Schema: <query: string> . Searches the internet for factual, current or unknown information."
    input_schema = WebSearchInput

    async def run(self , input_data : WebSearchInput) :
        #print(type(input_data))
        #print(input_data)
        client = TavilyClient(api_key = settings.tavily_api_key)
        query = input_data.query
        #print(query)
        try :
            response = client.search(query = query , search_depth = "basic" , max_results = 1)
            results = []
            #print(response)
            #print(type(response))
            for item in response.get("results" , []) :
                #print("inside loop")
                results.append({"title":item.get("title" , "")})
                results.append({"content":item.get("content" , "")})
                results.append({"url":item.get("url" , "")})
            #print(results)
            return ToolResult(
                success=True ,
                output = {
                    "query" : query ,
                    "results" : results
                }
            )
        except Exception as e :
            print("returned from web_search.py line34")
            return ToolResult(
                success=False ,
                error = str(e)
            )


    



