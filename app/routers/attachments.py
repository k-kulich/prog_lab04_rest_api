from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, Response, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestError, NotFoundError, field_error_message
from app.models import Attachment, Homework, Lesson
from app.schemas import AttachmentCreate, AttachmentOut, AttachmentUpdate

router = APIRouter(prefix="/api/attachments", tags=["attachments"])


def _out(a: Attachment) -> Dict[str, Any]:
    return AttachmentOut.model_validate(a).model_dump(mode="json")


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and len(payload) == 1:
        return payload[key]
    return payload


def _validate(model_cls, data: dict):
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as e:
        raise BadRequestError(field_error_message(e.errors()[0]))


def _check_owner(db: Session, lesson_id: Optional[int], homework_id: Optional[int]) -> None:
    has_lesson = lesson_id is not None
    has_homework = homework_id is not None
    if has_lesson == has_homework:
        raise BadRequestError(
            "Exactly one of 'lesson_id' or 'homework_id' must be provided"
        )
    if has_lesson and db.get(Lesson, lesson_id) is None:
        raise BadRequestError(
            f"Field 'lesson_id' refers to non-existing lesson id={lesson_id}"
        )
    if has_homework and db.get(Homework, homework_id) is None:
        raise BadRequestError(
            f"Field 'homework_id' refers to non-existing homework id={homework_id}"
        )


@router.get("")
def list_attachments(db: Session = Depends(get_db)):
    rows = db.execute(select(Attachment).order_by(Attachment.id)).scalars().all()
    return {"list": [_out(a) for a in rows]}


@router.get("/{att_id}")
def get_attachment(att_id: int, db: Session = Depends(get_db)):
    a = db.get(Attachment, att_id)
    if a is None:
        raise NotFoundError("Attachment", att_id)
    return {"attachment": _out(a)}


@router.post("")
def create_attachment(payload: dict = Body(...), db: Session = Depends(get_db)):
    data = _validate(AttachmentCreate, _unwrap(payload, "attachment"))
    _check_owner(db, data.lesson_id, data.homework_id)
    a = Attachment(**data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"attachment": _out(a)}


@router.patch("/{att_id}")
def update_attachment(att_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    a = db.get(Attachment, att_id)
    if a is None:
        raise NotFoundError("Attachment", att_id)
    data = _validate(AttachmentUpdate, _unwrap(payload, "attachment"))
    changes = data.model_dump(exclude_unset=True)
    new_lesson = changes.get("lesson_id", a.lesson_id)
    new_homework = changes.get("homework_id", a.homework_id)
    if "lesson_id" in changes or "homework_id" in changes:
        _check_owner(db, new_lesson, new_homework)
    for k, v in changes.items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return {"attachment": _out(a)}


@router.delete("/{att_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_attachment(att_id: int, db: Session = Depends(get_db)):
    a = db.get(Attachment, att_id)
    if a is None:
        raise NotFoundError("Attachment", att_id)
    db.delete(a)
    db.commit()
    return Response(status_code=status.HTTP_202_ACCEPTED)