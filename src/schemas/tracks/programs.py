# src/schemas/news/newsletter.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from models.track import CourseBase, MediaMeta, ModuleBase, ModuleContentBase, TrackBase


class TrackCreate(TrackBase):
	pass


class TrackOut(TrackBase):
	public_id: UUID
	created: datetime | None = None
	updated: datetime | None = None


class CourseCreate(CourseBase):
	pass


class CourseOut(BaseModel):
	id: int
	public_id: UUID
	title: str
	description: str | None = None
	order: int | None = None
	theme: str | None = None
	track: TrackOut
	created: datetime | None = None
	updated: datetime | None = None


class CourseUpdate(BaseModel):
	public_track_id: UUID | None = None  # Optional for updates
	title: str | None = None  # Optional for updates
	description: str | None = None
	order: int | None = None
	theme: str | None = None


class MediaMetaData(MediaMeta):
	pass


class ContentMediaCreate(BaseModel):
	name: str
	position: int
	url: str
	meta: MediaMetaData | None = None


class ContentMediaOut(BaseModel):
	public_id: UUID
	caption: str
	position: int
	url: str
	meta: dict | None = None
	created: datetime | None = None
	updated: datetime | None = None


class ContentMediaUpdate(BaseModel):
	caption: str | None = None
	position: int | None = None
	url: str | None = None
	meta: MediaMetaData | None = None


class ModuleCreate(ModuleBase):
	pass


class ModuleOut(ModuleBase):
	public_id: UUID
	created: datetime | None = None
	updated: datetime | None = None


class ModuleUpdate(BaseModel):
	name: str | None = None
	description: str | None = None
	order: int | None = None


class ModuleContentCreate(ModuleContentBase):
	media: list[ContentMediaCreate] | None = None


class ModuleContentOut(BaseModel):
	title: str
	summary: str | None = None
	markdown: str | None = None
	primary_media_url: str | None = None
	cover_image_url: str | None = None
	order: int | None = None
	draft: bool
	is_published: bool
	published_at: datetime | None = None
	estimated_minutes: int | None = None
	tags: list[str] | None = None
	media: list[ContentMediaOut] | None = None
	created: datetime | None = None
	updated: datetime | None = None


class ModuleContentUpdate(BaseModel):
	title: str | None = None
	summary: str | None = None
	markdown: str | None = None
	primary_media_url: str | None = None
	cover_image_url: str | None = None
	order: int | None = None
	draft: bool | None = None
	is_published: bool | None = None
	published_at: datetime | None = None
	estimated_minutes: int | None = None
	tags: list[str] | None = None
	media: list[ContentMediaUpdate] | None = None


class ModuleCompositeIn(BaseModel):
	module: ModuleCreate
	contents: ModuleContentCreate | None = None


class ModuleCompositeOut(BaseModel):
	module: ModuleOut
	contents: list[ModuleContentOut] | None = None


class ModuleCompositeUpdate(BaseModel):
	module: ModuleUpdate | None = None
	contents: list[ModuleContentUpdate] | None = None
