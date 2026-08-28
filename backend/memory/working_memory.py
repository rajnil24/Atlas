from dataclasses import dataclass
from backend.db.redis import redis_client
import json

@dataclass
class Turn:
    role: str      # "user" | "assistant"
    content: str


class WorkingMemory:
    """Session-scoped, in-process buffer. Caps by approximate token count,
    not message count, so it degrades gracefully regardless of message size."""

    def __init__(self, session_id , max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.session_id = session_id 
        self.redis_client = redis_client 

    @property
    def key(self) -> str:
        return f"session:{self.session_id}:working_memory"

    def add_turn(self, role: str, content: str):
        turns = self._load_turns()
        turns.append({
            "role": role,
            "content": content,
        })
        total = sum(
            self._estimate_tokens(turn["content"])
            for turn in turns
        )
        while total > self.max_tokens and len(turns) > 1:
            removed = turns.pop(0)
            total -= self._estimate_tokens(
                removed["content"]
            )
        self._save_turns(turns)

    def _load_turns(self) -> list[dict]:
        data = self.redis_client.get(self.key)
        if data is None:
            return []
        return json.loads(data)

    def _save_turns(self, turns: list[dict]) -> None:
        self.redis_client.set(
            self.key,
            json.dumps(turns),
        )

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
    
    def get_turns(self) -> list[dict]:
        return self._load_turns()

    def get_turn_count(self) -> int:
        return len(self._load_turns())

    def get_formatted_history(self) -> str:
        turns = self._load_turns()
        if not turns:
            return "No prior conversation in this session."
        return "\n".join(
            f"[{turn['role']}] {turn['content']}"
            for turn in turns
        )

    def clear(self):
        self.redis_client.delete(self.key)