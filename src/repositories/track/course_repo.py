from sqlalchemy import func
from sqlmodel import UUID, Session, select

from models.track.programs import Course
from repositories import get_public_id


class CourseRepository:
	"""CRUD repository for Course."""

	def __init__(self, db: Session):
		self.db = db

	# -------- getters --------
	def get(self, pk: int) -> Course | None:
		stmt = select(Course).where(Course.id == pk)
		return self.db.exec(stmt).first()

	def get_all(self, *, limit: int, offset: int = 0) -> list[Course]:
		stmt = select(Course).limit(limit).offset(offset)
		return self.db.exec(stmt).all()

	def get_by_public_id(self, public_id: str | UUID, *, include_deleted: bool = False) -> Course | None:
		public_id_str = str(public_id)
		return get_public_id(
			self.db,
			Course,
			public_id_str,
			include_deleted=include_deleted,
		)

	def count(self) -> int:
		stmt = select(func.count()).select_from(Course)
		return int(self.db.exec(stmt).one())

	# -------- mutations --------
	def create(self, payload: dict) -> Course:
		obj = Course(**payload)
		self.db.add(obj)
		self.db.commit()
		self.db.refresh(obj)
		return obj

	def update(self, public_id, payload: dict) -> Course | None:
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

	def soft_delete(self, public_id: UUID) -> None:
		obj = self.get_by_public_id(public_id)
		if not obj:
			return
		obj.is_deleted = True
		self.db.commit()
		self.db.refresh(obj)
