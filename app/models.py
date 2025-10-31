from pydantic import BaseModel, Field
from typing import Optional
class Token(BaseModel): access_token: str; token_type: str = "bearer"
class TokenData(BaseModel): username: Optional[str] = None
class User(BaseModel): username: str; disabled: bool = False
class DenoiseQuery(BaseModel):
    strength: float = Field(0.6, ge=0.0, le=1.0)
    model_name: str = Field("ddpm")
