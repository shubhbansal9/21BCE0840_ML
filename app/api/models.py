from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    text: str
    top_k: int
    threshold: float
    user_id: str

class SearchResponse(BaseModel):
    results: List[dict]
    inference_time: float