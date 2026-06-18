from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

# --- Requests ---

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    company_name: str = Field(..., min_length=2, max_length=100)

class UserLoginRequest(BaseModel):
        email: EmailStr
        password: str

# --- Responses ---
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    tenant_id: UUID
    role: str

class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    subscription_tier: str