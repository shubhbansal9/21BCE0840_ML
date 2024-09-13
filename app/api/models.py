from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    text: str
    top_k: int = 5
    threshold: float = 0.5
    user_id: str

class SearchResult(BaseModel):
    id: str
    content: str
    score: float