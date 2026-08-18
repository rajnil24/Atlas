#from groq import Groq
from backend.config import GEMINI_API_KEY 
import asyncio
from google import genai
class LLMClient:

    def __init__(self):

        self.client = genai.Client(api_key = GEMINI_API_KEY )
        self.model = "gemini-3.6-flash"

    
    async def generate(self, prompt: str) -> str:

        response = await self.client.aio.models.generate_content(

            model=self.model,

            contents=prompt,

        )
        return response.text
    
    async def synthesize_response(self, prompt: str) -> str:
        response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
        return response.text

    async def generate_response(self, messages: list) -> str:

        response = await self.client.aio.models.generate_content(
                    model=self.model, 
                    contents=messages,  
                )
        return response.text


llm = LLMClient()
resp = asyncio.run(llm.generate("hello"))
print(resp)