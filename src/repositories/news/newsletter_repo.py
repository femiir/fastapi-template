# src/repos/newsletter_repo.py
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Session, select

from models.news import NewsletterSubscriber


def _normalize_email(email: str) -> str:
	return email.strip().lower()


class NewsletterRepository:
	"""Lean repository: stage objects; caller controls commit."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int, *, include_deleted: bool = False) -> NewsletterSubscriber | None:
		stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.id == pk)
		if (not include_deleted) and hasattr(NewsletterSubscriber, 'is_deleted'):
			stmt = stmt.where(NewsletterSubscriber.is_deleted.is_(False))
		return self.db.exec(stmt).first()

	def get_by_email(self, email: EmailStr, include_deleted: bool = False) -> NewsletterSubscriber | None:
		stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
		if (not include_deleted) and hasattr(NewsletterSubscriber, 'is_deleted'):
			stmt = stmt.where(NewsletterSubscriber.is_deleted.is_(False))
		return self.db.exec(stmt).first()

	def get_by_public_id(
		self, public_id: str | UUID, *, include_deleted: bool = False
	) -> NewsletterSubscriber | None:
		public_id_str = str(public_id)  # ensure string to match varchar column
		stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.public_id == public_id_str)
		if (not include_deleted) and hasattr(NewsletterSubscriber, 'is_deleted'):
			stmt = stmt.where(NewsletterSubscriber.is_deleted.is_(False))
		return self.db.exec(stmt).first()

	def get_all(
		self,
		*,
		limit: int,
		offset: int = 0,
		include_deleted: bool = False,
	) -> list[NewsletterSubscriber]:
		"""Windowed fetch with limit/offset (non-deleted by default)."""
		stmt = select(NewsletterSubscriber)
		if (not include_deleted) and hasattr(NewsletterSubscriber, 'is_deleted'):
			stmt = stmt.where(NewsletterSubscriber.is_deleted.is_(False))
		stmt = stmt.limit(limit).offset(offset)
		return self.db.exec(stmt).all()

	def count(self, *, include_deleted: bool = False) -> int:
		stmt = select(func.count()).select_from(NewsletterSubscriber)
		if (not include_deleted) and hasattr(NewsletterSubscriber, 'is_deleted'):
			stmt = stmt.where(NewsletterSubscriber.is_deleted.is_(False))
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, email: EmailStr) -> NewsletterSubscriber:
		email = _normalize_email(email)
		sub = NewsletterSubscriber(email=email)
		self.db.add(sub)
		self.db.commit()
		self.db.refresh(sub)
		return sub

	# -------- soft deletes --------
	def soft_delete(self, public_id: str | UUID) -> None:
		public_id_str = str(public_id)  # ensure string to match varchar column
		stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.public_id == public_id_str)
		sub = self.db.exec(stmt).first()
		if sub:
			sub.is_active = False
			sub.is_deleted = True
			sub.unsubscribed_at = func.now()
			self.db.add(sub)
			self.db.commit()
			self.db.refresh(sub)

	# -------- restores --------
	def restore(self, email: EmailStr) -> None:
		stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
		sub = self.db.exec(stmt).first()
		if sub:
			sub.is_active = True
			sub.is_deleted = False
			self.db.add(sub)
			self.db.commit()
			self.db.refresh(sub)
