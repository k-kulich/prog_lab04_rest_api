from __future__ import annotations
from datetime import date, datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TutorBase(BaseModel):
    fio: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=50)
    bio: Optional[str] = Field(None, max_length=500)

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Field 'email' should be a valid email address")
        return v


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    fio: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        if v is None:
            return v
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Field 'email' should be a valid email address")
        return v


class TutorOut(TutorBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class StudentBase(BaseModel):
    fio: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    birth_date: date
    grade_level: int = Field(..., ge=1, le=11)
    tutor_id: int = Field(..., ge=1)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    fio: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None
    grade_level: Optional[int] = Field(None, ge=1, le=11)
    tutor_id: Optional[int] = Field(None, ge=1)


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


LessonStatus = Literal["scheduled", "done", "cancelled"]


class LessonBase(BaseModel):
    title: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=50)
    topic: Optional[str] = Field(None, max_length=200)
    start_at: datetime
    duration_min: int = Field(..., ge=15, le=240)
    lesson_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    status: LessonStatus = "scheduled"
    tutor_id: int = Field(..., ge=1)
    student_id: int = Field(..., ge=1)


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=50)
    topic: Optional[str] = Field(None, max_length=200)
    start_at: Optional[datetime] = None
    duration_min: Optional[int] = Field(None, ge=15, le=240)
    lesson_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[LessonStatus] = None
    tutor_id: Optional[int] = Field(None, ge=1)
    student_id: Optional[int] = Field(None, ge=1)


class LessonOut(LessonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


HomeworkStatus = Literal["assigned", "submitted", "graded"]


class HomeworkBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: date
    status: HomeworkStatus = "assigned"
    grade: Optional[int] = Field(None, ge=0, le=100)
    lesson_id: int = Field(..., ge=1)


class HomeworkCreate(HomeworkBase):
    pass


class HomeworkUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[date] = None
    status: Optional[HomeworkStatus] = None
    grade: Optional[int] = Field(None, ge=0, le=100)
    lesson_id: Optional[int] = Field(None, ge=1)


class HomeworkOut(HomeworkBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


AttachmentKind = Literal["link", "file", "material"]


class AttachmentBase(BaseModel):
    kind: AttachmentKind
    name: str = Field(..., max_length=200)
    url: str = Field(..., max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    lesson_id: Optional[int] = Field(None, ge=1)
    homework_id: Optional[int] = Field(None, ge=1)


class AttachmentCreate(AttachmentBase):
    pass


class AttachmentUpdate(BaseModel):
    kind: Optional[AttachmentKind] = None
    name: Optional[str] = Field(None, max_length=200)
    url: Optional[str] = Field(None, max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    lesson_id: Optional[int] = Field(None, ge=1)
    homework_id: Optional[int] = Field(None, ge=1)


class AttachmentOut(AttachmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int