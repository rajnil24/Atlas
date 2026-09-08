from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str