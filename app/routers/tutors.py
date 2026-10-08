from typing import Any, Dict

from fastapi import APIRouter, Body, Depends, Response, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import BadRequestError, NotFoundError, field_error_message
from app.models import Lesson, Student, Tutor
from app.schemas import LessonOut, StudentOut, TutorCreate, TutorOut, TutorUpdate

router = APIRouter(prefix="/api/tutors", tags=["tutors"])


def _out(t: Tutor) -> Dict[str, Any]:
    return TutorOut.model_validate(t).model_dump(mode="json")


def _unwrap(payload: dict, key: str) -> dict:
    if isinstance(payload, dict) and key in payload and len(payload) == 1:
        return payload[key]
    return payload


def _validate(model_cls, data: dict):
    try:
        return model_cls.model_validate(data)
    except PydanticValidationError as e:
        raise BadRequestError(field_error_message(e.errors()[0]))


@router.get("")
def list_tutors(db: Session = Depends(get_db)):
    tutors = db.execute(select(Tutor).order_by(Tutor.id)).scalars().all()
    return {"list": [_out(t) for t in tutors]}


@router.get("/{tutor_id}")
def get_tutor(tutor_id: int, db: Session = Depends(get_db)):
    t = db.get(Tutor, tutor_id)
    if t is None:
        raise NotFoundError("Tutor", tutor_id)
    return {"tutor": _out(t)}


@router.post("")
def create_tutor(payload: dict = Body(...), db: Session = Depends(get_db)):
    data = _validate(TutorCreate, _unwrap(payload, "tutor"))
    tutor = Tutor(**data.model_dump())
    db.add(tutor)
    db.commit()
    db.refresh(tutor)
    return {"tutor": _out(tutor)}


@router.patch("/{tutor_id}")
def update_tutor(tutor_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    t = db.get(Tutor, tutor_id)
    if t is None:
        raise NotFoundError("Tutor", tutor_id)
    data = _validate(TutorUpdate, _unwrap(payload, "tutor"))
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return {"tutor": _out(t)}


@router.delete("/{tutor_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_tutor(tutor_id: int, db: Session = Depends(get_db)):
    t = db.get(Tutor, tutor_id)
    if t is None:
        raise NotFoundError("Tutor", tutor_id)
    db.delete(t)
    db.commit()
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/{tutor_id}/students")
def list_tutor_students(tutor_id: int, db: Session = Depends(get_db)):
    t = db.get(Tutor, tutor_id)
    if t is None:
        raise NotFoundError("Tutor", tutor_id)
    rows = db.execute(
        select(Student).where(Student.tutor_id == tutor_id).order_by(Student.id)
    ).scalars().all()
    return {"list": [StudentOut.model_validate(s).model_dump(mode="json") for s in rows]}


@router.get("/{tutor_id}/lessons")
def list_tutor_lessons(tutor_id: int, db: Session = Depends(get_db)):
    t = db.get(Tutor, tutor_id)
    if t is None:
        raise NotFoundError("Tutor", tutor_id)
    rows = db.execute(
        select(Lesson).where(Lesson.tutor_id == tutor_id).order_by(Lesson.id)
    ).scalars().all()
    return {"list": [LessonOut.model_validate(l).model_dump(mode="json") for l in rows]}