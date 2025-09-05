from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from dependencies import DbSession, Pagination

# (Module model not directly used in router; imported indirectly in service.)
from repositories.track.module_composite import ModuleCompositeService
from schemas import (
	Paginated,
	ResponseBase,
	ResponseData,
	make_data_response,
	make_paginated_response,
	make_response,
)
from schemas.tracks import ModuleCompositeIn, ModuleCompositeOut, ModuleCompositeUpdate, ModuleOut

router = APIRouter(prefix='/modules', tags=['Modules'])


@router.get('/', response_model=Paginated[ModuleOut], status_code=status.HTTP_200_OK)
def list_modules(db: DbSession, pagination: Pagination):
	"""Paginated list of modules (without contents/media)."""
	raw_items = ModuleCompositeService.get_all(db, limit=pagination.limit, offset=pagination.offset)
	items = [ModuleOut.model_validate(o, from_attributes=True) for o in raw_items]
	total = ModuleCompositeService.count(db)
	return make_paginated_response(
		items=items,
		total=total,
		limit=pagination.limit,
		offset=pagination.offset,
		message='Modules retrieved successfully.',
		status_code=status.HTTP_200_OK,
	)


"""Composite serialization handled by service layer; helpers removed for brevity."""


@router.get('/{public_id}/', response_model=ResponseData[ModuleCompositeOut], status_code=status.HTTP_200_OK)
def get_module_composite(public_id: UUID, db: DbSession):
	"""Retrieve a full composite (module + contents + media)."""
	composite = ModuleCompositeService.get_module_composite(db, public_id)
	if not composite:
		raise HTTPException(status_code=404, detail='Module not found')
	return make_data_response(
		composite,
		status_code=status.HTTP_200_OK,
		message='Composite module retrieved successfully',
	)


@router.post('/', response_model=ResponseData[ModuleCompositeOut], status_code=status.HTTP_201_CREATED)
def create_module_composite(payload: ModuleCompositeIn, db: DbSession):
	composite = ModuleCompositeService.create_module_composite(db, payload)
	return make_data_response(
		composite, status_code=status.HTTP_201_CREATED, message='Composite module created'
	)


@router.patch('/{public_id}/', response_model=ResponseData[ModuleCompositeOut], status_code=status.HTTP_200_OK)
def update_module_composite(public_id: UUID, payload: ModuleCompositeUpdate, db: DbSession):
	composite = ModuleCompositeService.update_module_composite(db, public_id, payload)
	if not composite:
		raise HTTPException(status_code=404, detail='Module not found')
	return make_data_response(composite, status_code=status.HTTP_200_OK, message='Composite module updated')


@router.delete('/{public_id}/', response_model=ResponseBase, status_code=status.HTTP_200_OK)
def delete_module_composite(public_id: UUID, db: DbSession):
	deleted = ModuleCompositeService.delete_module_composite(db, public_id)
	if not deleted:
		raise HTTPException(status_code=404, detail='Module not found')
	return make_response(status_code=status.HTTP_200_OK, success=True, message='Composite module deleted')
