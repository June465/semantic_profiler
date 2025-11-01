from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str = Field(..., description="The unique username for the user.")

class UserCreate(UserBase):
    password: str = Field(..., description="The user's password (will be hashed).")

class UserInDB(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True