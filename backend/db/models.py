from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float
from pgvector.sqlalchemy import Vector
from backend.db.connection import Base

EMBEDDING_DIM = 384  

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class Fact(Base):
    __tablename__ = "facts"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    fact_text = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
    category = Column(String, index=True)
    confidence = Column(Float, default=1.0)
    source_episode_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))