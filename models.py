"""Item models."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ItemCreate(BaseModel):
    """Model for creating items."""
    name: str


class Item(BaseModel):
    """Item model."""
    id: int
    name: str
    created_at: datetime