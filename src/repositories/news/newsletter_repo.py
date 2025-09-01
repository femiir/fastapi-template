# src/repositories/news/newsletter_repo.py

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime

from sqlmodel import Session, select

from models.news import NewsletterSubscriber

# ---------------------------------------------------------------------------
#  Get
# ---------------------------------------------------------------------------


def get_by_id(db: Session, subscriber_id: int) -> NewsletterSubscriber | None:
	return db.get(NewsletterSubscriber, subscriber_id)


def get_by_public_id(db: Session, public_id: str) -> NewsletterSubscriber | None:
	stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.public_id == public_id)
	return db.exec(stmt).first()


def get_by_email(db: Session, email: str) -> NewsletterSubscriber | None:
	stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
	return db.exec(stmt).first()

# ---------------------------------------------------------------------------
#  Create
# ---------------------------------------------------------------------------


def create_subscriber(session: Session, email: str) -> tuple[NewsletterSubscriber, bool, bool]:
	"""Create a new subscriber.

	Returns tuple: (subscriber, created, reactivated)
	  - created=True if a brand new row was inserted
	  - reactivated=True if an existing inactive subscriber was reactivated
	If the email already exists and is active, returns existing with flags False/False.
	"""
	email = email.lower().strip()
	existing = get_by_email(session, email)
	if existing:
		if not existing.is_active:
			existing.is_active = True
			existing.unsubscribed_at = None
			session.add(existing)
			return existing, False, True
		return existing, False, False

	subscriber = NewsletterSubscriber(email=email)
	session.add(subscriber)
	session.flush()
	session.refresh(subscriber)
	return subscriber, True, False


# ---------------------------------------------------------------------------
# Update (confirmation / unsubscribe / generic status changes)
# ---------------------------------------------------------------------------


def unsubscribe(session: Session, subscriber: NewsletterSubscriber) -> bool:
	"""Soft-unsubscribe a subscriber.

	Returns True if a change was applied, False if already inactive.
	"""
	if not subscriber.is_active:
		return False
	subscriber.is_active = False
	subscriber.unsubscribed_at = datetime.now(datetime.UTC)
	session.add(subscriber)
	return True


def reactivate(session: Session, subscriber: NewsletterSubscriber) -> bool:
	"""Reactivate an inactive subscriber.

	Returns True if reactivated, False if already active.
	"""
	if subscriber.is_active:
		return False
	subscriber.is_active = True
	subscriber.unsubscribed_at = None
	session.add(subscriber)
	return True


# ---------------------------------------------------------------------------
# Listing / Counting
# ---------------------------------------------------------------------------


def list_subscribers(
	session: Session,
	*,
	limit: int = 50,
	offset: int = 0,
	active: bool | None = None,
	search_email: str | None = None,
	order_desc: bool = True,
) -> Sequence[NewsletterSubscriber]:
	"""Return a page of subscribers.

	NOTE: Does not return total count (pair with count_subscribers if needed).
	"""
	stmt = select(NewsletterSubscriber)
	if active is not None:
		stmt = stmt.where(NewsletterSubscriber.is_active == active)
	if search_email:
		like = f'%{search_email.lower()}%'
		stmt = stmt.where(NewsletterSubscriber.email.ilike(like))  # Postgres ILIKE
	if order_desc:
		stmt = stmt.order_by(NewsletterSubscriber.id.desc())
	else:
		stmt = stmt.order_by(NewsletterSubscriber.id.asc())
	stmt = stmt.limit(limit).offset(offset)
	return session.exec(stmt).all()


def count_subscribers(
	session: Session,
	*,
	active: bool | None = None,
	search_email: str | None = None,
) -> int:
	from sqlalchemy import func
	from sqlmodel import select as sql_select

	stmt = sql_select(func.count(NewsletterSubscriber.id))
	if active is not None or search_email:
		# Build base selectable with filters
		base = select(NewsletterSubscriber.id)
		if active is not None:
			base = base.where(NewsletterSubscriber.is_active == active)
		if search_email:
			like = f'%{search_email.lower()}%'
			base = base.where(NewsletterSubscriber.email.ilike(like))
		stmt = sql_select(func.count()).select_from(base.subquery())
	return session.exec(stmt).one()


# ---------------------------------------------------------------------------
# Bulk utilities
# ---------------------------------------------------------------------------


def batch_get_by_emails(session: Session, emails: Iterable[str]) -> list[NewsletterSubscriber]:
	if not emails:
		return []
	stmt = select(NewsletterSubscriber).where(NewsletterSubscriber.email.in_(list(emails)))
	return list(session.exec(stmt).all())


__all__ = [
	'batch_get_by_emails',
	'count_subscribers',
	'create_subscriber',
	'get_by_email',
	'get_by_id',
	'get_by_public_id',
	'list_subscribers',
	'reactivate',
	'unsubscribe',
]
