import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import Base, engine
from app.exceptions import BadRequestError, NotFoundError, bad_request_handler, internal_handler, not_found_handler, validation_handler
from app.routers import attachments, homework, lessons, students, tutors


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not os.environ.get("TESTING"):
        from app import models  # noqa: F401

        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_title, version="1.0.0", lifespan=lifespan)

app.add_exception_handler(RequestValidationError, validation_handler)
app.add_exception_handler(NotFoundError, not_found_handler)
app.add_exception_handler(BadRequestError, bad_request_handler)
app.add_exception_handler(Exception, internal_handler)

app.include_router(tutors.router)
app.include_router(students.router)
app.include_router(lessons.router)
app.include_router(homework.router)
app.include_router(attachments.router)


@app.get("/health")
def health():
    return {"status": "ok"}