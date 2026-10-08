from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, Response, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestError, NotFoundError, field_error_message
from app.models import Attachment, Homework, Lesson, Student, Tutor
from app.schemas import AttachmentOut, HomeworkOut, LessonCreate, LessonOut, LessonUpdate

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _out(l: Lesson) -> Dict[str, Any]:
    return LessonOut.model_validate(l).model_dump(mode="json")


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and len(payload) == 1:
        return payload[key]
    return payload


def _validate(model_cls, data: dict):
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as e:
        raise BadRequestError(field_error_message(e.errors()[0]))


def _check_fks(db: Session, tutor_id: int, student_id: int):
    if db.get(Tutor, tutor_id) is None:
        raise BadRequestError(f"Field 'tutor_id' refers to non-existing tutor id={tutor_id}")
    st = db.get(Student, student_id)
    if st is None:
        raise BadRequestError(f"Field 'student_id' refers to non-existing student id={student_id}")
    if st.tutor_id != tutor_id:
        raise BadRequestError(
            f"Student id={student_id} does not belong to tutor id={tutor_id}"
        )


@router.get("")
def list_lessons(db: Session = Depends(get_db)):
    rows = db.execute(select(Lesson).order_by(Lesson.id)).scalars().all()
    return {"list": [_out(l) for l in rows]}


@router.get("/{lesson_id}")
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    l = db.get(Lesson, lesson_id)
    if l is None:
        raise NotFoundError("Lesson", lesson_id)
    return {"lesson": _out(l)}


@router.post("")
def create_lesson(payload: dict = Body(...), db: Session = Depends(get_db)):
    data = _validate(LessonCreate, _unwrap(payload, "lesson"))
    _check_fks(db, data.tutor_id, data.student_id)
    l = Lesson(**data.model_dump())
    db.add(l)
    db.commit()
    db.refresh(l)
    return {"lesson": _out(l)}


@router.patch("/{lesson_id}")
def update_lesson(lesson_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    l = db.get(Lesson, lesson_id)
    if l is None:
        raise NotFoundError("Lesson", lesson_id)
    data = _validate(LessonUpdate, _unwrap(payload, "lesson"))
    changes = data.model_dump(exclude_unset=True)
    new_tutor = changes.get("tutor_id", l.tutor_id)
    new_student = changes.get("student_id", l.student_id)
    if "tutor_id" in changes or "student_id" in changes:
        _check_fks(db, new_tutor, new_student)
    for k, v in changes.items():
        setattr(l, k, v)
    db.commit()
    db.refresh(l)
    return {"lesson": _out(l)}


@router.delete("/{lesson_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    l = db.get(Lesson, lesson_id)
    if l is None:
        raise NotFoundError("Lesson", lesson_id)
    db.delete(l)
    db.commit()
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/{lesson_id}/homework")
def list_lesson_homework(lesson_id: int, db: Session = Depends(get_db)):
    l = db.get(Lesson, lesson_id)
    if l is None:
        raise NotFoundError("Lesson", lesson_id)
    rows = db.execute(
        select(Homework).where(Homework.lesson_id == lesson_id).order_by(Homework.id)
    ).scalars().all()
    return {"list": [HomeworkOut.model_validate(h).model_dump(mode="json") for h in rows]}


@router.get("/{lesson_id}/attachments")
def list_lesson_attachments(lesson_id: int, db: Session = Depends(get_db)):
    l = db.get(Lesson, lesson_id)
    if l is None:
        raise NotFoundError("Lesson", lesson_id)
    rows = db.execute(
        select(Attachment).where(Attachment.lesson_id == lesson_id).order_by(Attachment.id)
    ).scalars().all()
    return {"list": [AttachmentOut.model_validate(a).model_dump(mode="json") for a in rows]}