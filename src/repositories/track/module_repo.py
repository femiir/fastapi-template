from sqlalchemy import func
from sqlmodel import UUID, Session, select
from fastapi import HTTPException

from models.track.programs import ContentMedia, Module, ModuleContent
from repositories import get_public_id


class ModuleRepository:
	"""CRUD repository for Module."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int) -> Module | None:
		stmt = select(Module).where(Module.id == pk)
		return self.db.exec(stmt).first()

	def get_by_public_id(self, public_id: str | UUID, *, include_deleted: bool = False) -> Module | None:
		public_id_str = str(public_id)
		return get_public_id(
			self.db,
			Module,
			public_id_str,
			include_deleted=include_deleted,
		)

	def get_all(self, *, limit: int, offset: int = 0) -> list[Module]:
		stmt = select(Module).limit(limit).offset(offset)
		return self.db.exec(stmt).all()

	def count(self) -> int:
		stmt = select(func.count()).select_from(Module)
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, payload: dict) -> Module:
		obj = Module(**payload)
		self.db.add(obj)
		self.db.commit()

		self.db.refresh(obj)
		return obj

	def update(self, public_id: UUID, payload: dict) -> Module | None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return None

		for field, value in payload.items():
			if value is not None:
				setattr(obj, field, value)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def delete(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return
		self.db.delete(obj)
		self.db.commit()


class ModuleContentRepository:
	"""CRUD repository for ModuleContent."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int) -> ModuleContent | None:
		stmt = select(ModuleContent).where(ModuleContent.id == pk)
		return self.db.exec(stmt).first()

	def get_by_public_id(self, public_id: str | UUID, *, include_deleted: bool = False) -> ModuleContent | None:
		public_id_str = str(public_id)
		return get_public_id(
			self.db,
			ModuleContent,
			public_id_str,
			include_deleted=include_deleted,
		)

	def get_all(self, *, limit: int, offset: int = 0) -> list[ModuleContent]:
		stmt = select(ModuleContent).limit(limit).offset(offset)
		return self.db.exec(stmt).all()

	def count(self) -> int:
		stmt = select(func.count()).select_from(ModuleContent)
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, payload: dict) -> ModuleContent:
		obj = ModuleContent(**payload)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def update(self, public_id: UUID, payload: dict) -> ModuleContent | None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return None

		for field, value in payload.items():
			if value is not None:
				setattr(obj, field, value)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def delete(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return
		self.db.delete(obj)
		self.db.commit()


class ContentMediaRepository:
	"""CRUD repository for ContentMedia (media assets for module content)."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int) -> ContentMedia | None:
		stmt = select(ContentMedia).where(ContentMedia.id == pk)
		return self.db.exec(stmt).first()

	def get_by_public_id(self, public_id: str | UUID, *, include_deleted: bool = False) -> ContentMedia | None:
		public_id_str = str(public_id)
		return get_public_id(
			self.db,
			ContentMedia,
			public_id_str,
			include_deleted=include_deleted,
		)

	def get_all(
		self, *, limit: int, offset: int = 0, module_content_public_id: UUID | None = None
	) -> list[ContentMedia]:
		stmt = select(ContentMedia).limit(limit).offset(offset)
		if module_content_public_id is not None:
			stmt = stmt.where(ContentMedia.module_content_public_id == module_content_public_id)
		return self.db.exec(stmt).all()

	def count(self) -> int:
		stmt = select(func.count()).select_from(ContentMedia)
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, payload: dict) -> ContentMedia:
		obj = ContentMedia(**payload)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def update(self, public_id: UUID, payload: dict) -> ContentMedia | None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return None

		for field, value in payload.items():
			if value is not None:
				setattr(obj, field, value)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def delete(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return
		self.db.delete(obj)
		self.db.commit()
