# src/schemas/news/newsletter.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class SubscribeIn(BaseModel):
	email: EmailStr


class Unsubscribe(BaseModel):
	public_id: UUID


class SubscriberOut(BaseModel):
	id: int
	public_id: UUID
	email: EmailStr
	is_active: bool
	unsubscribed_at: datetime | None
	created: datetime
	updated: datetime
