from dataclasses import dataclass, field


@dataclass
class Turn:
    role: str      # "user" | "assistant"
    content: str


class WorkingMemory:
    """Session-scoped, in-process buffer. Caps by approximate token count,
    not message count, so it degrades gracefully regardless of message size."""

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.turns: list[Turn] = []

    def add_turn(self, role: str, content: str):
        self.turns.append(Turn(role=role, content=content))
        self._trim()

    def _estimate_tokens(self, text: str) -> int:
        # rough heuristic: ~4 characters per token for English text.
        # Not exact, but good enough to prevent unbounded growth cheaply,
        # without calling a real tokenizer on every single turn.
        return max(1, len(text) // 4)

    def _trim(self):
        total = sum(self._estimate_tokens(t.content) for t in self.turns)
        while total > self.max_tokens and len(self.turns) > 1:
            removed = self.turns.pop(0)   # drop oldest first
            total -= self._estimate_tokens(removed.content)

    def get_formatted_history(self) -> str:
        if not self.turns:
            return "No prior conversation in this session."
        return "\n".join(f"[{t.role}] {t.content}" for t in self.turns)

    def clear(self):
        self.turns = []