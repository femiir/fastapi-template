# src/models/news/newsletter.py

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Boolean, Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, SQLModel

from models import TimestampMixin


class NewsletterSubscriber(TimestampMixin, SQLModel, table=True):
	"""Represents a newsletter subscription."""

	__tablename__ = 'newsletter_subscribers'
	__table_args__ = (UniqueConstraint('email', name='uq_newsletter_email'),)

	id: int | None = Field(default=None, primary_key=True)

	public_id: UUID = Field(
		default_factory=uuid4,
		sa_column=Column(String(36), unique=True, nullable=False, index=True),
		description='Stable UUID for external links (unsubscribe / confirm)',
	)

	email: EmailStr = Field(
		sa_column=Column(String(320), nullable=False, unique=True, index=True),
		description='Subscriber email address (unique)',
	)

	is_active: bool = Field(
		default=True,
		sa_column=Column(Boolean, nullable=False, server_default='true'),
		description='Whether subscription currently active (false if unsubscribed)',
	)

	unsubscribed_at: datetime | None = Field(
		default=None,
		sa_column=Column(DateTime(timezone=True), nullable=True),
		description='Timestamp when user unsubscribed',
	)

	# created / updated provided by TimestampMixin

	def __repr__(self) -> str:  # pragma: no cover - simple debug helper
		return f'<NewsletterSubscriber id={self.id} email={self.email} active={self.is_active}>'
