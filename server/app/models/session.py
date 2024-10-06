from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .song import Song
from .user import User


class Session(BaseModel):
    id: Optional[str] = None
    name: str
    host_id: Optional[str] = None
    host_name: Optional[str] = None
    guests: dict[str, User] = {}
    invite_link: Optional[str] = None
    playlist: list[Song] = []
    creation_date: Optional[datetime] = None
    recommendations: dict[str, list[str]] = {}
    # is_running: bool = False
