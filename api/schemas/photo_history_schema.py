from pydantic import BaseModel

class PhotoHistoryBase(BaseModel):
    date: str
    photo: str
    description: str | None = None
    plant_id: int

class PhotoHistoryCreate(PhotoHistoryBase):
    pass

class PhotoHistoryResponse(PhotoHistoryBase):
    id: int

    class Config:
        orm_mode = True
