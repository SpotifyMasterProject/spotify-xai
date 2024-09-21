from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .song import Song


class Session(BaseModel):
    id: Optional[str] = None
    name: str
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    guests: list[str] = []
    invite_link: Optional[str] = None
    playlist: list[Song] = []
    creation_date: Optional[datetime] = None
    # is_running: bool = False
