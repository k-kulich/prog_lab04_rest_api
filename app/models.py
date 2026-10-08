from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.base import Base


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    subject: Mapped[str] = mapped_column(String(50))
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    students: Mapped[list["Student"]] = relationship(
        back_populates="tutor", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="tutor", cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    birth_date: Mapped[date] = mapped_column(Date)
    grade_level: Mapped[int] = mapped_column(Integer)
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), index=True
    )

    tutor: Mapped[Tutor] = relationship(back_populates="students")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(50))
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime)
    duration_min: Mapped[int] = mapped_column(Integer, default=60)
    lesson_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutors.id", ondelete="CASCADE"), index=True
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), index=True
    )

    tutor: Mapped[Tutor] = relationship(back_populates="lessons")
    student: Mapped[Student] = relationship(back_populates="lessons")
    homework: Mapped[list["Homework"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        foreign_keys="Attachment.lesson_id",
    )


class Homework(Base):
    __tablename__ = "homework"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    due_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="assigned")
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), index=True
    )

    lesson: Mapped[Lesson] = relationship(back_populates="homework")
    attachments: Mapped[list["Attachment"]] = relationship(
        back_populates="homework",
        cascade="all, delete-orphan",
        foreign_keys="Attachment.homework_id",
    )


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    kind: Mapped[str] = mapped_column(String(20))
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(1000))
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    lesson_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True
    )
    homework_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("homework.id", ondelete="CASCADE"), nullable=True, index=True
    )

    lesson: Mapped[Optional[Lesson]] = relationship(
        back_populates="attachments", foreign_keys=[lesson_id]
    )
    homework: Mapped[Optional[Homework]] = relationship(
        back_populates="attachments", foreign_keys=[homework_id]
    )