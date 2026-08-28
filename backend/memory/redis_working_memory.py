import json

class RedisWorkingMemory:

    def __init__(self, redis_client, session_id: str):
        self.redis = redis_client
        self.session_id = session_id

    @property
    def key(self) -> str:
        return f"session:{self.session_id}:working_memory"

    def save(self, turns: list[dict]) -> None:
        self.redis.set(
            self.key,
            json.dumps(turns),
        )

    def load(self) -> list[dict]:
        data = self.redis.get(self.key)

        if data is None:
            return []

        return json.loads(data)

    def clear(self) -> None:
        self.redis.delete(self.key)

from backend.db.redis import redis_client
redis = redis_client
redis_working_memory = RedisWorkingMemory(redis  , session_id = "123")

turns = [

    {

        "role": "user",

        "content": "What is PostgreSQL?"

    },

    {

        "role": "assistant",

        "content": "PostgreSQL is a relational database."

    },

]

redis_working_memory.save(turns)

loaded = redis_working_memory.load()

print(loaded)