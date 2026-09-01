import json
from sentence_transformers import SentenceTransformer
from backend.memory.episode_store import EpisodicStore
from backend.memory.semantic_store import SemanticStore
from backend.services.llm import LLMClient

EXTRACTOR_PROMPT = """
You are a memory extraction system. Your job is to read a slice of
conversation and decide what, if anything, is worth remembering
long-term about the user.

Recent conversation (user messages, assistant responses, and relevant
tool results):

{episode_text}

Rules:

1. Only extract facts that are STABLE and likely to remain true or
   relevant beyond this single conversation (preferences, ongoing
   plans, identity/context facts, recurring commitments).
2. Do NOT extract: one-off requests, small talk, facts already stated
   in a way that's clearly temporary, or anything you're inferring
   without clear support in the text.
3. Each fact must be a single, self-contained, clearly stated
   sentence -- rewrite messy or indirect statements into a clean fact.
4. Assign a category: one of "wedding", "work", "preference",
   "placement_prep", "project", "other".
5. Assign a confidence between 0 and 1: how certain are you this is
   accurate and durable, based only on the text given.
6. If nothing in this conversation is worth remembering, return an
   empty list.

Return ONLY valid JSON, no explanation, matching this schema:

{{
    "facts": [
        {{
            "fact_text": "",
            "category": "",
            "confidence": 0.0
        }}
    ]
}}
"""

_embedding_model = None

def get_embedding_model():

    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

class Extractor:
    def __init__(self):
        self.episodic_store = EpisodicStore()
        self.semantic_store = SemanticStore()
        self.llm = LLMClient()

    async def run(self, user_id: str, session_id: str, episode_limit: int = 20):
        episodes = self.episodic_store.get_session_history(session_id, limit=episode_limit)
        print("inside extractor line 57")
        if not episodes:
            return []

        relevant = [e for e in episodes if e.role in ("user", "assistant")]
        if not relevant:
            return []

        episode_text = "\n".join(f"[{e.role}] {e.content}" for e in reversed(relevant))
        print("episode_text is " , episode_text)
        prompt = EXTRACTOR_PROMPT.format(episode_text=episode_text)
        print("prompt is\n " , prompt)
        raw_response =  await self.llm.generate_response(prompt)
        raw_response = raw_response.replace("```json" , "")
        raw_response = raw_response.replace("```" , "")
        raw_response = raw_response.strip()
        print("raw_response is " , raw_response)
        try:
            parsed = json.loads(raw_response)
            print("parsing done")
            candidates = parsed.get("facts", [])
            print("candidates are , " , candidates )
        except (json.JSONDecodeError, AttributeError):
            print("[Extractor] failed to parse LLM output, skipping this batch")
            return []

        written_ids = []
        for candidate in candidates:
            fact_text = candidate.get("fact_text", "").strip()
            if not fact_text:
                continue

            embedding = get_embedding_model().encode(fact_text).tolist()

            fact_id = self.semantic_store.upsert_fact(
                user_id=user_id,
                fact_text=fact_text,
                embedding=embedding,
                category=candidate.get("category", "other"),
                confidence=float(candidate.get("confidence", 0.5)),
                source_episode_id=relevant[0].id,
            )
            if fact_id:
                written_ids.append(fact_id)

        return written_ids