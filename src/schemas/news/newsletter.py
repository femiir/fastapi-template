# src/schemas/news/newsletter.py

from pydantic import EmailStr, BaseModel
from datetime import datetime
from uuid import UUID

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
	created_at: datetime
	updated_at: datetime