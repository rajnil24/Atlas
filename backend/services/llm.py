from groq import Groq
from backend.config import GROQ_API_KEY


class LLMClient:

    def __init__(self):

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    async def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
        return response.choices[0].message.content
    
    async def synthesize_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
        return response.choices[0].message.content

    async def generate_response(self, messages: list) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content