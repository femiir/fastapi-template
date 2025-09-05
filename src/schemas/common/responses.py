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


class PaginationParams(BaseModel):
	limit: int
	offset: int

	@property
	def slice(self) -> tuple[int, int]:
		return self.limit, self.offset


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


def make_paginated_response[T](
	items: Sequence[T],
	total: int,
	limit: int,
	offset: int,
	message: str = 'Request successful',
	status_code: int = 200,
) -> Paginated[T]:
	pages = (total // limit + (1 if total % limit else 0)) if limit else None
	meta = PageMeta(
		total=total,
		limit=limit,
		offset=offset,
		pages=pages,
	)
	return Paginated[T](
		success=True,
		status_code=status_code,
		message=message,
		meta=meta,
		items=items,
	)
