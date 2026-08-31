from sentence_transformers import SentenceTransformer
from backend.memory.semantic_store import SemanticStore


class MemoryRetriever:

    def __init__(self, min_confidence: float = 0.4, top_k: int = 5):
        self.semantic_store = SemanticStore()
        self.min_confidence = min_confidence
        self.top_k = top_k
        self._embedding_model = None

    def _get_embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        return self._embedding_model

    async def get_relevant_facts(
        self,
        user_id: str,
        query: str,
    ) -> list[str]:

        embedding_model = self._get_embedding_model()

        query_embedding = embedding_model.encode(query).tolist()

        facts = self.semantic_store.retrieve(
            user_id=user_id,
            query_embedding=query_embedding,
            top_k=self.top_k,
        )

        filtered = [
            f
            for f in facts
            if f.confidence >= self.min_confidence
        ]

        return [f.fact_text for f in filtered]

    def format_for_prompt(self, facts: list[str]) -> str:
        if not facts:
            return "No known facts about this user yet."

        return "\n".join(
            f"- {fact}" for fact in facts
        )