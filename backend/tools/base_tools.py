from abc import ABC, abstractmethod
from typing import Any, Optional, Type
from pydantic import BaseModel


class ToolResult(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None


class BaseTool(ABC):
    """
    Every Atlas tool must inherit from this class.
    """

    tool_name: str
    tool_description: str

    # Pydantic model describing expected input.
    input_schema: Type[BaseModel]

    @abstractmethod
    async def run(
        self,
        input_data: dict
    ) -> ToolResult:
        pass