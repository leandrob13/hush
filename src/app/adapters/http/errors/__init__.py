from __future__ import annotations

from typing import Any, List
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError


class DtoValidationError(BaseModel):
    error: Any

    @staticmethod
    def from_request_validation_error_dict(error: Any) -> DtoValidationError:
        # err = list
        return DtoValidationError(
            error=error,
        )


class DtoValidationErrors(BaseModel):
    errors: List[DtoValidationError]
    body: Any

    @staticmethod
    def from_request_validation_error(
        exc: RequestValidationError,
    ) -> DtoValidationErrors:
        return DtoValidationErrors(
            body=exc.body,
            errors=[
                DtoValidationError.from_request_validation_error_dict(error)
                for error in exc.errors()
            ],
        )
