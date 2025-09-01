# src/db/pagination.py
from collections.abc import Sequence
from math import ceil
from typing import Any

from sqlalchemy import func
from sqlalchemy.sql import Select
from sqlmodel import Session, select

from dependencies import PaginationParams
from schemas import PageMeta, Paginated


def paginate_select(
	session: Session,
	stmt: Select,
	paginator: PaginationParams,
	*,
	count: bool = True,
	total_override: int | None = None,
) -> tuple[Sequence[Any], int | None]:
	# page data
	rows = session.exec(stmt.limit(paginator.limit).offset(paginator.offset)).all()

	if total_override is not None:
		return rows, total_override
	if not count:
		return rows, None

	# optimized COUNT(*): remove ORDER BY, wrap original stmt as subquery
	count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
	total = session.exec(count_stmt).scalar_one()
	return rows, int(total)


def build_paginated_response(
	items: Sequence[Any],
	total: int | None,
	paginator: PaginationParams,
) -> Paginated[Any]:
	pages = None if total is None else (ceil(total / paginator.limit) if paginator.limit else 0)
	meta = PageMeta(
		total=total,
		limit=paginator.limit,
		offset=paginator.offset,
		pages=pages,
	)
	return Paginated(
		success=True,
		status_code=200,
		message=None,
		meta=meta,
		items=items,
	)


def paginate(
	session: Session,
	stmt: Select,
	params: PaginationParams,
	*,
	count: bool = True,
	total_override: int | None = None,
) -> Paginated[Any]:
	items, total = paginate_select(session, stmt, params, count=count, total_override=total_override)
	return build_paginated_response(items, total, params)
