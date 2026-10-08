from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    def __init__(self, entity: str, obj_id: Any):
        self.entity = entity
        self.id = obj_id


class BadRequestError(Exception):
    def __init__(self, reason: str):
        self.reason = reason


def field_error_message(err: dict) -> str:
    loc = err.get("loc", ())
    field = loc[-1] if loc else "field"
    t = err.get("type", "")
    ctx = err.get("ctx", {}) or {}

    if t == "missing":
        return f"Field '{field}' is required"
    if t == "string_too_long":
        return f"Field '{field}' should be at most {ctx.get('max_length')} characters"
    if t == "string_too_short":
        return f"Field '{field}' should be at least {ctx.get('min_length')} characters"
    if t == "greater_than_equal":
        return f"Field '{field}' should be greater or equal then {ctx.get('ge')}"
    if t == "greater_than":
        return f"Field '{field}' should be greater then {ctx.get('gt')}"
    if t == "less_than_equal":
        return f"Field '{field}' should be less then {ctx.get('le')}"
    if t == "less_than":
        return f"Field '{field}' should be less then {ctx.get('lt')}"
    if t in ("int_parsing", "int_type"):
        return f"Field '{field}' should be an integer"
    if t in ("float_parsing", "float_type"):
        return f"Field '{field}' should be a number"
    if t == "date_from_datetime_parsing":
        return f"Field '{field}' should be a date (YYYY-MM-DD)"
    if t in ("date_parsing", "date_type"):
        return f"Field '{field}' should be a date (YYYY-MM-DD)"
    if t in ("datetime_parsing", "datetime_type"):
        return f"Field '{field}' should be a datetime (ISO 8601)"
    if t in ("string_type", "str_type"):
        return f"Field '{field}' should be a string"
    if t == "literal_error":
        expected = ctx.get("expected", "a valid value")
        return f"Field '{field}' should be one of {expected}"
    if t == "value_error":
        err_obj = ctx.get("error")
        if err_obj is not None:
            return str(err_obj)
        return err.get("msg", "invalid value")
    if t == "json_invalid":
        return "Request body should be valid JSON"
    return f"Field '{field}' is invalid: {err.get('msg', 'unknown error')}"


async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    reason = field_error_message(errors[0]) if errors else "Validation error"
    return JSONResponse(status_code=400, content={"status": 400, "reason": reason})


async def not_found_handler(_: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": 404, "reason": f"{exc.entity} with id={exc.id} not found"},
    )


async def bad_request_handler(_: Request, exc: BadRequestError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": 400, "reason": exc.reason},
    )


async def internal_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": 500, "reason": str(exc) or exc.__class__.__name__},
    )