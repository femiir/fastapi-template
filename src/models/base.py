# src/models/base.py

from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
	"""
	Simple reusable mixin:
	- created / updated: server-managed timestamps
	- is_deleted: soft delete flag
	No explicit Column objects -> no reuse conflicts.
	"""

	is_deleted: bool = Field(default=False, description='Soft delete marker (False = active)')

	created: datetime | None = Field(
		default=None,
		sa_column_kwargs={
			'nullable': False,
			'server_default': func.now(),
		},
		description='Row creation timestamp',
	)

	updated: datetime | None = Field(
		default=None,
		sa_column_kwargs={
			'nullable': False,
			'server_default': func.now(),
			'onupdate': func.now(),
		},
		description='Last modification timestamp',
	)
