from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, Response, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestError, NotFoundError, field_error_message
from app.models import Homework, Lesson, Student, Tutor
from app.schemas import HomeworkOut, LessonOut, StudentCreate, StudentOut, StudentUpdate

router = APIRouter(prefix="/api/students", tags=["students"])


def _out(s: Student) -> Dict[str, Any]:
    return StudentOut.model_validate(s).model_dump(mode="json")


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and len(payload) == 1:
        return payload[key]
    return payload


def _validate(model_cls, data: dict):
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as e:
        raise BadRequestError(field_error_message(e.errors()[0]))


def _ensure_tutor(db: Session, tutor_id: int):
    if db.get(Tutor, tutor_id) is None:
        raise BadRequestError(f"Field 'tutor_id' refers to non-existing tutor id={tutor_id}")


@router.get("")
def list_students(db: Session = Depends(get_db)):
    rows = db.execute(select(Student).order_by(Student.id)).scalars().all()
    return {"list": [_out(s) for s in rows]}


@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    s = db.get(Student, student_id)
    if s is None:
        raise NotFoundError("Student", student_id)
    return {"student": _out(s)}


@router.post("")
def create_student(payload: dict = Body(...), db: Session = Depends(get_db)):
    data = _validate(StudentCreate, _unwrap(payload, "student"))
    _ensure_tutor(db, data.tutor_id)
    s = Student(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"student": _out(s)}


@router.patch("/{student_id}")
def update_student(student_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    s = db.get(Student, student_id)
    if s is None:
        raise NotFoundError("Student", student_id)
    data = _validate(StudentUpdate, _unwrap(payload, "student"))
    changes = data.model_dump(exclude_unset=True)
    if "tutor_id" in changes:
        _ensure_tutor(db, changes["tutor_id"])
    for k, v in changes.items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return {"student": _out(s)}


@router.delete("/{student_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    s = db.get(Student, student_id)
    if s is None:
        raise NotFoundError("Student", student_id)
    db.delete(s)
    db.commit()
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/{student_id}/lessons")
def list_student_lessons(student_id: int, db: Session = Depends(get_db)):
    s = db.get(Student, student_id)
    if s is None:
        raise NotFoundError("Student", student_id)
    rows = db.execute(
        select(Lesson).where(Lesson.student_id == student_id).order_by(Lesson.id)
    ).scalars().all()
    return {"list": [LessonOut.model_validate(l).model_dump(mode="json") for l in rows]}


@router.get("/{student_id}/homework")
def list_student_homework(student_id: int, db: Session = Depends(get_db)):
    s = db.get(Student, student_id)
    if s is None:
        raise NotFoundError("Student", student_id)
    rows = db.execute(
        select(Homework)
        .join(Lesson, Homework.lesson_id == Lesson.id)
        .where(Lesson.student_id == student_id)
        .order_by(Homework.id)
    ).scalars().all()
    return {"list": [HomeworkOut.model_validate(h).model_dump(mode="json") for h in rows]}