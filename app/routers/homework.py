from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, Response, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestError, NotFoundError, field_error_message
from app.models import Attachment, Homework, Lesson
from app.schemas import AttachmentOut, HomeworkCreate, HomeworkOut, HomeworkUpdate

router = APIRouter(prefix="/api/homework", tags=["homework"])


def _out(h: Homework) -> Dict[str, Any]:
    return HomeworkOut.model_validate(h).model_dump(mode="json")


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and len(payload) == 1:
        return payload[key]
    return payload


def _validate(model_cls, data: dict):
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as e:
        raise BadRequestError(field_error_message(e.errors()[0]))


def _ensure_lesson(db: Session, lesson_id: int):
    if db.get(Lesson, lesson_id) is None:
        raise BadRequestError(f"Field 'lesson_id' refers to non-existing lesson id={lesson_id}")


@router.get("")
def list_homework(db: Session = Depends(get_db)):
    rows = db.execute(select(Homework).order_by(Homework.id)).scalars().all()
    return {"list": [_out(h) for h in rows]}


@router.get("/{hw_id}")
def get_homework(hw_id: int, db: Session = Depends(get_db)):
    h = db.get(Homework, hw_id)
    if h is None:
        raise NotFoundError("Homework", hw_id)
    return {"homework": _out(h)}


@router.post("")
def create_homework(payload: dict = Body(...), db: Session = Depends(get_db)):
    data = _validate(HomeworkCreate, _unwrap(payload, "homework"))
    _ensure_lesson(db, data.lesson_id)
    h = Homework(**data.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return {"homework": _out(h)}


@router.patch("/{hw_id}")
def update_homework(hw_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    h = db.get(Homework, hw_id)
    if h is None:
        raise NotFoundError("Homework", hw_id)
    data = _validate(HomeworkUpdate, _unwrap(payload, "homework"))
    changes = data.model_dump(exclude_unset=True)
    if "lesson_id" in changes:
        _ensure_lesson(db, changes["lesson_id"])
    for k, v in changes.items():
        setattr(h, k, v)
    db.commit()
    db.refresh(h)
    return {"homework": _out(h)}


@router.delete("/{hw_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_homework(hw_id: int, db: Session = Depends(get_db)):
    h = db.get(Homework, hw_id)
    if h is None:
        raise NotFoundError("Homework", hw_id)
    db.delete(h)
    db.commit()
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/{hw_id}/attachments")
def list_homework_attachments(hw_id: int, db: Session = Depends(get_db)):
    h = db.get(Homework, hw_id)
    if h is None:
        raise NotFoundError("Homework", hw_id)
    rows = db.execute(
        select(Attachment).where(Attachment.homework_id == hw_id).order_by(Attachment.id)
    ).scalars().all()
    return {"list": [AttachmentOut.model_validate(a).model_dump(mode="json") for a in rows]}