# src/api/tracks/track_router.py
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from dependencies import DbSession, Pagination
from models import Track
from repositories import TrackRepository
from schemas import (
	Paginated,
	ResponseBase,
	ResponseData,
	make_data_response,
	make_paginated_response,
	make_response,
)
from schemas.tracks import TrackCreate, TrackOut

router = APIRouter(prefix='/tracks', tags=['Tracks'])


@router.post('/', response_model=ResponseData[Track], status_code=status.HTTP_201_CREATED)
async def create_track(payload: TrackCreate, db: DbSession):
	repo = TrackRepository(db)
	existing = repo.get_by_name(payload.name, include_deleted=True)
	if existing:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Track name already exists')
	obj = repo.create(payload.model_dump())
	return make_data_response(
		Track.model_validate(obj, from_attributes=True),
		status_code=status.HTTP_201_CREATED,
		message='Track created successfully',
	)


@router.get('/', response_model=Paginated[TrackOut], status_code=status.HTTP_200_OK)
async def list_all_tracks(db: DbSession, pagination: Pagination):
	repo = TrackRepository(db)
	raw_items = repo.get_all(limit=pagination.limit, offset=pagination.offset)

	items = [TrackOut.model_validate(obj, from_attributes=True) for obj in raw_items]

	total = repo.count()

	return make_paginated_response(
		items=items,
		total=total,
		limit=pagination.limit,
		offset=pagination.offset,
		message='Tracks retrieved successfully.',
		status_code=status.HTTP_200_OK,
	)


@router.patch('/{public_id}/', response_model=ResponseData[TrackOut], status_code=status.HTTP_200_OK)
async def update_track(public_id: UUID, payload: TrackCreate, db: DbSession):
	repo = TrackRepository(db)
	existing = repo.get_by_public_id(public_id, include_deleted=True)

	if not existing:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track not found')
	obj = repo.update(public_id, payload.model_dump())
	return make_data_response(
		TrackOut.model_validate(obj, from_attributes=True),
		status_code=status.HTTP_200_OK,
		message='Track updated successfully',
	)


@router.delete('/{public_id}/', response_model=ResponseBase, status_code=status.HTTP_200_OK)
async def delete_track(public_id: UUID, db: DbSession):
	repo = TrackRepository(db)
	existing = repo.get_by_public_id(public_id)
	if not existing:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Track not found')
	repo.soft_delete(public_id)
	return make_response(
		status_code=status.HTTP_204_NO_CONTENT, success=True, message='Track deleted successfully.'
	)
