from backend.memory.retriever import MemoryRetriever
from backend.memory.episode_store import EpisodicStore
class ContextBuilder:
    """Assembles the final context sent to the planner, enforcing
    a total token budget across working memory + retrieved facts."""

    def __init__(self, working_memory , total_budget: int = 3000):
        self.working_memory = working_memory
        self.retriever = MemoryRetriever(min_confidence = 0.4 , top_k = 5)
        self.episodic_store = EpisodicStore()
        self.total_budget = total_budget

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    async def build(self, user_id: str, session_id: str, query: str) -> dict:
        query_tokens = self._estimate_tokens(query)
        remaining = self.total_budget - query_tokens

        facts = await self.retriever.get_relevant_facts(user_id, query)
        facts_text = self.retriever.format_for_prompt(facts)
        facts_tokens = self._estimate_tokens(facts_text)

        if facts_tokens > remaining:
            while facts and self._estimate_tokens(self.retriever.format_for_prompt(facts)) > remaining:
               facts.pop()
            facts_text = self.retriever.format_for_prompt(facts)
            facts_tokens = self._estimate_tokens(facts_text)

        remaining -= facts_tokens

        history_text = self.working_memory.get_formatted_history()

        # Fallback: if working memory is thin (new session / just restarted),
        # pull recent episodes from Postgres so context isn't empty
        if self.working_memory.get_turn_count() < 2:
            recent_episodes = self.episodic_store.get_session_history(session_id, limit=5)
            if recent_episodes:
               history_text = "\n".join(
                  f"[{e.role}] {e.content}" for e in reversed(recent_episodes)
               )

        history_tokens = self._estimate_tokens(history_text)

        if history_tokens > remaining:
            history_text = history_text[: remaining * 4]  # crude character-level trim as last resort

        return {
            "known_facts": facts_text,
            "conversation_history": history_text,
        }