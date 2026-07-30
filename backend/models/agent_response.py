from dataclasses import dataclass, field


@dataclass
class AgentResponse:

    reply: str

    tools_used: list[str] = field(default_factory=list)

    execution_time: float = 0.0

    success: bool = True

    error: str | None = None