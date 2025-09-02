# src/dependencies/db_session.py

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from db.conf import SessionLocal


def get_session() -> Generator[Session]:
	db = SessionLocal()
	try:
		yield db
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()


# Type alias for injection
DbSession = Annotated[Session, Depends(get_session)]
