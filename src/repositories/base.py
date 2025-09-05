from uuid import UUID

from sqlmodel import Session, SQLModel, select


def get_public_id(
	db: Session, model: type[SQLModel], public_id: str | UUID, *, include_deleted: bool = False
) -> SQLModel | None:
	"""Generic function to fetch a record by public_id."""
	public_id_str = str(public_id)  # ensure string to match varchar column
	stmt = select(model).where(model.public_id == public_id_str)
	if (not include_deleted) and hasattr(model, 'is_deleted'):
		stmt = stmt.where(model.is_deleted.is_(False))
	return db.exec(stmt).first()
