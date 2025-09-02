# src/dependencies/pagination.py

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Query

from schemas import PaginationParams

DEFAULT_LIMIT = 50
MAX_LIMIT = 200


# ---- FASTAPI DEPENDENCY (inject into endpoints) ----
def pagination_params(
	limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
	offset: int = Query(0, ge=0),
) -> PaginationParams:
	return PaginationParams(limit=limit, offset=offset)


Pagination = Annotated[PaginationParams, Depends(pagination_params)]
