# src/models/track/programs.py

"""
Imagine you're building a digital university with tracks (programs), courses, topics, content (articles/lectures), and media (videos, slides, images).

Track → like a degree program (Frontend, Backend, Data Science).

Course → like a class inside the program (FastAPI 101, Intro to Databases).

Module (previously Topic) → like a chapter/module inside the course (Authentication, Queries, ORM).

CourseContent → like a lecture note / blog post (actual material written in Markdown).

CourseMedia → like images/videos/slides attached to the lecture.

Frontend -> React=>
track -Backend -> courses - fastapi, python, database 101==>selected_course =python->topic-datatypes-\notes on topic and materials and videos
Data Science -> Python, R
"""

# CourseContent → like a lecture note / blog post (actual material written in Markdown).

# CourseMedia → like images/videos/slides attached to the lecture.

# Frontend -> React=>
# track -Backend -> courses - fastapi, python, database 101==>selected_course =python->topic-datatypes-\notes on topic and materials and videos
# Data Science -> Python, R
# """

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlalchemy import JSON, Column, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from models import TimestampMixin


class TrackBase(SQLModel):
	name: str = Field(index=True)
	description: str | None = None
	theme: str | None = None

	# Field validator to ensure name is always lowercase
	@field_validator('name', mode='before')
	@classmethod
	def validate_name(cls, value: str) -> str:
		if value is not None:
			return value.strip().lower()  # Strip whitespace and convert to lowercase
		return value


class Track(TrackBase, TimestampMixin, table=True):
	__tablename__ = 'tracks'
	__table_args__ = (UniqueConstraint('name'),)

	id: int | None = Field(default=None, primary_key=True)
	public_id: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)
	courses: list['Course'] = Relationship(back_populates='track')


class CourseBase(SQLModel):
	track_public_id: UUID = Field(foreign_key='tracks.public_id', index=True, nullable=False)
	title: str
	description: str | None = None
	order: int | None = Field(default=None, index=True, ge=1)
	theme: str | None = None

	@field_validator('theme', mode='before')
	@classmethod
	def validate_theme(cls, value: str) -> str:
		if value is not None:
			return value.strip().lower()
		return value

	@field_validator('title', mode='before')
	@classmethod
	def validate_title(cls, value: str) -> str:
		if value is not None:
			return value.strip().lower()
		return value


class Course(CourseBase, TimestampMixin, SQLModel, table=True):
	__tablename__ = 'courses'
	__table_args__ = (
		UniqueConstraint('track_public_id', 'order'),
		UniqueConstraint('track_public_id', 'title'),
	)

	id: int | None = Field(default=None, primary_key=True)
	public_id: UUID = Field(
		default_factory=uuid4,
		index=True,
		unique=True,
		nullable=False,
		description='Stable UUID for external links',
	)
	track: Track = Relationship(back_populates='courses')


class ModuleBase(SQLModel):
	name: str = Field(index=True)
	description: str | None = None
	order: int | None = Field(default=None, index=True, ge=1)


class Module(ModuleBase, TimestampMixin, SQLModel, table=True):
	__tablename__ = 'modules'
	__table_args__ = (
		UniqueConstraint('name'),
		UniqueConstraint('name', 'order'),
		UniqueConstraint('public_id'),
	)
	id: int | None = Field(default=None, primary_key=True)
	public_id: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)

	# Add relationship to ModuleContent
	contents: list['ModuleContent'] = Relationship(back_populates='module')


class MediaMeta(SQLModel):
	ext: str | None = Field(default=None, description='File extension, e.g. mp4, jpg')
	size: int | None = Field(default=None, description='File size in bytes')
	media_type: str | None = Field(default=None, description='MIME type, e.g. video/mp4, image/jpeg')
	dimensions: dict[str, int] | None = Field(
		default=None,
		sa_column=Column(JSON, nullable=True),
		description='Media dimensions (width, height) in pixels',
	)


class ContentMediaBase(SQLModel):
	# Map 'caption' attribute to existing DB column 'name' to avoid migration for now
	caption: str = Field(sa_column=Column('name', String, nullable=False))
	position: int
	url: str
	meta: dict | None = Field(
		default=None,
		sa_column=Column(JSON, nullable=True),
		description='Metadata for the content media',
	)


class ContentMedia(ContentMediaBase, TimestampMixin, SQLModel, table=True):
	__tablename__ = 'module_media'
	__table_args__ = (
		UniqueConstraint('public_id', 'position'),
		UniqueConstraint('public_id'),
	)
	id: int | None = Field(default=None, primary_key=True)
	public_id: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)
	module_content_public_id: UUID = Field(foreign_key='module_content.public_id', index=True)

	# Relationship back to ModuleContent
	content: 'ModuleContent' = Relationship(back_populates='media')


class ModuleContentBase(SQLModel, table=False):
	title: str
	summary: str | None = None
	markdown: str | None = Field(default=None)
	primary_media_url: str | None = None
	cover_image_url: str | None = None
	order: int | None = Field(default=None, index=True)

	tags: list[str] | None = Field(
		default=None,
		sa_column=Column(JSON, nullable=True),
		description='List of tag strings',
	)

	@field_validator('tags', mode='before')
	@classmethod
	def validate_tags(cls, validated):
		if not validated:
			return validated
		seen: set[str] = set()
		out: list[str] = []
		for raw in validated:
			if raw is None:
				continue
			norm = str(raw).strip().lower()
			if not norm or norm in seen:
				continue
			seen.add(norm)
			out.append(norm)
		return out


class ModuleContent(ModuleContentBase, TimestampMixin, SQLModel, table=True):
	__tablename__ = 'module_content'
	__table_args__ = (
		UniqueConstraint('public_id'),
		UniqueConstraint('module_public_id', 'order'),
	)
	id: int | None = Field(default=None, primary_key=True)
	public_id: UUID = Field(
		default_factory=uuid4,
		index=True,
		unique=True,
		nullable=False,
		description='Stable UUID for external links',
	)
	draft: bool = Field(default=True, index=True)
	is_published: bool = Field(default=False, index=True)
	published_at: datetime | None = Field(default=None, index=True)
	estimated_minutes: int | None = Field(default=None)
	module_public_id: UUID | None = Field(default=None, foreign_key='modules.public_id', index=True)

	# Singular relationship name; points back to Module.contents
	module: Optional['Module'] = Relationship(back_populates='contents')
	# List relationship to ContentMedia
	media: list['ContentMedia'] = Relationship(back_populates='content')
