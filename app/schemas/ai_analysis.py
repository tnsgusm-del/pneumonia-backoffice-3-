from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AiAnalysisResultResponse(BaseModel):
    id: int
    record_id: int
    is_pneumonia: bool
    confidence: float
    heatmap_url: Optional[str] = None
    ai_model: str
    created_at: datetime

    class Config:
        from_attributes = True
