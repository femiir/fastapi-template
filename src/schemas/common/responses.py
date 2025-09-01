# src/schemas/common/responses.py

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel, Field

# TypeVar for helper functions
T = TypeVar('T')


class ResponseBase(BaseModel):
	success: bool = Field(default=False)
	status_code: int = Field(..., description='HTTP status code')
	message: Any | None = Field(default=None, description='Readable message')


class ResponseData[T](ResponseBase):
	data: T | None = Field(default=None)


class PageMeta(BaseModel):
	total: int | None
	limit: int
	offset: int
	pages: int | None


class Paginated[T](ResponseBase):
	meta: PageMeta
	items: Sequence[T]


def make_response(
	status_code: int,
	success: bool,
	message: Any,
) -> ResponseBase:
	return ResponseBase(
		success=success,
		status_code=status_code,
		message=message,
	)


def make_data_response[T](
	data: T,
	status_code: int = 200,
	message: Any = None,
) -> ResponseData[T]:
	return ResponseData(
		success=True,
		status_code=status_code,
		message=message,
		data=data,
	)
