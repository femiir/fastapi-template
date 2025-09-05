from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from models import ContentMedia, Module, ModuleContent
from repositories.track.module_repo import ContentMediaRepository, ModuleContentRepository, ModuleRepository
from schemas.tracks import (
	ContentMediaOut,
	ModuleCompositeIn,
	ModuleCompositeOut,
	ModuleCompositeUpdate,
	ModuleContentOut,
	ModuleOut,
)

# ----------------- Serialization helpers -----------------


def _serialize_module(module: Module) -> ModuleOut:
	return ModuleOut.model_validate(module, from_attributes=True)


def _serialize_content(
	content: ModuleContent,
	*,
	module: Module | None = None,
	media: Sequence[ContentMedia] | None = None,
) -> ModuleContentOut:
	return ModuleContentOut.model_validate(
		{
			**content.model_dump(),
			'module': _serialize_module(module or content.module),
			'media': [
				ContentMediaOut.model_validate(m, from_attributes=True) for m in (media or content.media)
			],
		},
		from_attributes=True,
	)


def _serialize_composite(
	module: Module, contents: Sequence[ModuleContent], media_map: dict[UUID, list[ContentMedia]]
) -> ModuleCompositeOut:
	serialized_contents: list[ModuleContentOut] = [
		_serialize_content(c, module=module, media=media_map.get(c.public_id, [])) for c in contents
	]
	return ModuleCompositeOut(module=_serialize_module(module), contents=serialized_contents)


class ModuleCompositeService:
	@staticmethod
	def get_all(db: Session, *, limit: int, offset: int = 0) -> list[Module]:
		repo = ModuleRepository(db)
		return repo.get_all(limit=limit, offset=offset)

	@staticmethod
	def count(db: Session) -> int:
		repo = ModuleRepository(db)
		return repo.count()

	@staticmethod
	def create_module_composite(db: Session, payload: ModuleCompositeIn) -> ModuleCompositeOut:
		return create_module_composite(db, payload)

	@staticmethod
	def get_module_composite(db: Session, public_id: UUID) -> ModuleCompositeOut | None:
		return get_module_composite(db, public_id)

	@staticmethod
	def update_module_composite(
		db: Session, public_id: UUID, payload: ModuleCompositeUpdate
	) -> ModuleCompositeOut | None:
		return update_module_composite(db, public_id, payload)

	@staticmethod
	def delete_module_composite(db: Session, public_id: UUID) -> bool:
		return delete_module_composite(db, public_id)


# ----------------- Core operations -----------------


def create_module_composite(db: Session, payload: ModuleCompositeIn) -> ModuleCompositeOut:
	module_repo = ModuleRepository(db)
	content_repo = ModuleContentRepository(db)
	media_repo = ContentMediaRepository(db)

	module = module_repo.create(payload.module.model_dump())

	contents: list[ModuleContent] = []
	media_map: dict[UUID, list[ContentMedia]] = {}

	if payload.contents:
		content_payload = payload.contents.model_dump(exclude={'media'})
		content_payload['module_public_id'] = module.public_id
		content = content_repo.create(content_payload)
		contents.append(content)

		if payload.contents.media:
			for m in payload.contents.media:
				media_payload = m.model_dump()
				# Map name -> caption (DB column mapped to caption attribute)
				media_payload['caption'] = media_payload.pop('name')
				meta_val = media_payload.get('meta')
				if meta_val and hasattr(meta_val, 'model_dump'):
					media_payload['meta'] = meta_val.model_dump()
				media_payload['module_content_public_id'] = content.public_id
				media = media_repo.create(media_payload)
				media_map.setdefault(content.public_id, []).append(media)

	return _serialize_composite(module, contents, media_map)


def get_module_composite(db: Session, public_id: UUID) -> ModuleCompositeOut | None:
	module_repo = ModuleRepository(db)
	content_repo = ModuleContentRepository(db)
	media_repo = ContentMediaRepository(db)

	module = module_repo.get_by_public_id(public_id)
	if not module:
		return None

	contents = [c for c in content_repo.get_all(limit=500, offset=0) if c.module_public_id == module.public_id]
	media_map: dict[UUID, list[ContentMedia]] = {}
	for c in contents:
		media_items = media_repo.get_all(limit=500, offset=0, module_content_public_id=c.public_id)
		if media_items:
			media_map[c.public_id] = media_items

	return _serialize_composite(module, contents, media_map)


def update_module_composite(
	db: Session, public_id: UUID, payload: ModuleCompositeUpdate
) -> ModuleCompositeOut | None:
	module_repo = ModuleRepository(db)
	content_repo = ModuleContentRepository(db)
	media_repo = ContentMediaRepository(db)

	module = module_repo.get_by_public_id(public_id)
	if not module:
		return None

	if payload.module:
		module = module_repo.update(public_id, payload.module.model_dump(exclude_unset=True)) or module

	# NOTE: granular updates for nested contents/media not yet implemented
	contents = [c for c in content_repo.get_all(limit=500, offset=0) if c.module_public_id == module.public_id]
	all_media = media_repo.get_all(limit=1000, offset=0)
	media_map: dict[UUID, list[ContentMedia]] = {}
	valid_content_ids = {c.public_id for c in contents}
	for cm in all_media:
		if cm.module_content_public_id in valid_content_ids:
			media_map.setdefault(cm.module_content_public_id, []).append(cm)

	return _serialize_composite(module, contents, media_map)


def delete_module_composite(db: Session, public_id: UUID) -> bool:
	module_repo = ModuleRepository(db)
	content_repo = ModuleContentRepository(db)
	media_repo = ContentMediaRepository(db)

	module = module_repo.get_by_public_id(public_id)
	if not module:
		return False

	contents = [c for c in content_repo.get_all(limit=500, offset=0) if c.module_public_id == module.public_id]
	for c in contents:
		media_items = media_repo.get_all(limit=500, offset=0, module_content_public_id=c.public_id)
		for m in media_items:
			media_repo.delete(m.public_id)
		content_repo.delete(c.public_id)
	module_repo.delete(module.public_id)
	return True
