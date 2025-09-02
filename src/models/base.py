# src/models/base.py

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, func
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel, table=False):
	"""
	Reusable mixin:
	  created / updated managed by DB defaults + onupdate.
	  is_deleted soft delete flag.
	"""

	is_deleted: bool = Field(
		default=False,
		sa_column=Column(Boolean, nullable=False, server_default='false'),
		description='Soft delete marker (False = active)',
	)
	created: datetime = Field(
		sa_column=Column(
			DateTime(timezone=True),
			nullable=False,
			server_default=func.now(),
		),
		description='Row creation timestamp',
	)
	updated: datetime = Field(
		sa_column=Column(
			DateTime(timezone=True),
			nullable=False,
			server_default=func.now(),
			onupdate=func.now(),
		),
		description='Last modification timestamp',
	)

	def soft_delete(self) -> None:
		"""Mark row as deleted (no commit here)."""
		self.is_deleted = True

	def restore(self) -> None:
		"""Un-delete."""
		self.is_deleted = False

