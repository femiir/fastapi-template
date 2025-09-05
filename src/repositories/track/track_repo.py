# src/repositories/track/track_repo.py
from __future__ import annotations

from uuid import UUID

from sqlalchemy import func
from sqlmodel import Session, select

from models import Track
from repositories import get_public_id


class TrackRepository:
	"""CRUD repository for Track (lean: commits inside write ops like existing style)."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int, *, include_deleted: bool = False) -> Track | None:
		stmt = select(Track).where(Track.id == pk)
		if (not include_deleted) and hasattr(Track, 'is_deleted'):
			stmt = stmt.where(Track.is_deleted.is_(False))
		return self.db.exec(stmt).first()

	def get_by_name(self, name: str, *, include_deleted: bool = False) -> Track | None:
		stmt = select(Track).where(Track.name == name)
		if (not include_deleted) and hasattr(Track, 'is_deleted'):
			stmt = stmt.where(Track.is_deleted.is_(False))
		return self.db.exec(stmt).first()

	def get_by_public_id(self, public_id: str | UUID, *, include_deleted: bool = False) -> Track | None:
		public_id_str = str(public_id)
		return get_public_id(
			self.db,
			Track,
			public_id_str,
			include_deleted=include_deleted,
		)

	def get_all(
		self,
		*,
		limit: int,
		offset: int = 0,
		include_deleted: bool = False,
	) -> list[Track]:
		stmt = select(Track)
		if (not include_deleted) and hasattr(Track, 'is_deleted'):
			stmt = stmt.where(Track.is_deleted.is_(False))
		stmt = stmt.limit(limit).offset(offset)
		return self.db.exec(stmt).all()

	def count(self, *, include_deleted: bool = False) -> int:
		stmt = select(func.count()).select_from(Track)
		if (not include_deleted) and hasattr(Track, 'is_deleted'):
			stmt = stmt.where(Track.is_deleted.is_(False))
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, payload: dict) -> Track:
		obj = Track(**payload)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def update(self, public_id: UUID, payload: dict) -> Track | None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return None
		for key, value in payload.items():
			setattr(obj, key, value)
		self.db.commit()
		self.db.refresh(obj)
		return obj
	# -------- soft deletes --------

	def soft_delete(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return
		obj.is_deleted = True
		self.db.commit()
		self.db.refresh(obj)

	def restore(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id, include_deleted=True)
		if not obj:
			return
		obj.is_deleted = False
		self.db.commit()
		self.db.refresh(obj)
