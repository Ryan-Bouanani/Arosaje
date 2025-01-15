from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PhotoBase(BaseModel):
    filename: str
    url: str
    plant_id: int
    description: Optional[str] = None
    type: str  # 'plant', 'garde_start', 'garde_end'

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 