from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.models import Workload


class WorkersPostDTO(BaseModel):
    username: str


class WorkersGetDTO(BaseModel):
    id: int


class ResumesPostDTO(BaseModel):
    title: str
    compensation: Optional[int]
    workload: Workload
    worker_id: int


class ResumesGetDTO(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime


class ResumesRelDTO(ResumesGetDTO):
    worker: "WorkersGetDTO"


class WorkersRelDTO(WorkersGetDTO):
    resumes: list["ResumesGetDTO"]
