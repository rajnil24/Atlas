from backend.tools.base_tools import BaseTool

class ToolRegistry:

    def __init__(self):
        self.tools = {}
    # add tool , a function
    def register(self, tool: BaseTool):
        self.tools[tool.tool_name] = tool
    # get tools
    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)
    # show all available tools
    def list_tools(self):
        return list(self.tools.keys())
    
    def get_tools_description(self) :
        tools_description = []
        for tool in self.tools.values() :
            tools_description.append(
                {
                    "tool_name": tool.tool_name,
                    "description":tool.tool_description
                }
            )
        return tools_description

