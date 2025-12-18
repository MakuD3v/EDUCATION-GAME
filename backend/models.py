from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pydantic import BaseModel, ConfigDict
from .database import Base

# --- SQLAlchemy Models (DB) ---
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    elo: Mapped[int] = mapped_column(Integer, default=1000)
    
    # Relationships
    stats: Mapped[list["GameStat"]] = relationship(back_populates="user")

class GameStat(Base):
    __tablename__ = "game_stats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    wins: Mapped[int] = mapped_column(Integer, default=0)
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    
    user: Mapped["User"] = relationship(back_populates="stats")

# --- Pydantic Models (API) ---

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    elo: int
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
