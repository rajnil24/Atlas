from groq import Groq
from backend.config import settings 
from google import genai
import os 
class LLMClient:

    def __init__(self):
        """
        self.client = genai.Client(api_key = settings.gemini_api_key )
        self.model = "gemini-3.6-flash"
        """
        self.client = Groq(
            api_key=os.getenv("settings.groq_api_key")
        )

    async def generate(self, prompt: str) -> str:
        """
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text
        """
        response = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content

        
    async def synthesize_response(self, prompt: str) -> str:
        """
        response = await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
        return response.text
        """
        response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                    ]
                )
        return response.choices[0].message.content

     
    async def generate_response(self, messages: list) -> str:
        """
        response = await self.client.aio.models.generate_content(
                    model=self.model, 
                    contents=messages,  
                )
        return response.text
        """
        response = self.client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": messages
                            }
                            ]
                        )
        return response.choices[0].message.content
        


