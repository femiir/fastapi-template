# src/api/tracks/course_router.py
from fastapi import APIRouter, HTTPException, status

from dependencies import DbSession, Pagination
from repositories.track.course_repo import CourseRepository
from schemas import Paginated, ResponseBase, ResponseData, make_data_response, make_paginated_response
from schemas.tracks import CourseCreate, CourseOut, CourseUpdate

router = APIRouter(prefix='/courses', tags=['Courses'])


@router.post('/', response_model=ResponseData[CourseOut], status_code=status.HTTP_201_CREATED)
async def create_course(payload: CourseCreate, db: DbSession):
	repo = CourseRepository(db)
	obj = repo.create(payload.model_dump())
	return make_data_response(
		CourseOut.model_validate(obj, from_attributes=True),
		status_code=status.HTTP_201_CREATED,
		message='Course created successfully',
	)


@router.get('/', response_model=Paginated[CourseOut], status_code=status.HTTP_200_OK)
async def list_all_courses(db: DbSession, pagination: Pagination):
	repo = CourseRepository(db)
	raw_items = repo.get_all(limit=pagination.limit, offset=pagination.offset)
	items = [CourseOut.model_validate(obj, from_attributes=True) for obj in raw_items]
	total = repo.count()
	return make_paginated_response(
		items=items,
		total=total,
		limit=pagination.limit,
		offset=pagination.offset,
		message='Courses retrieved successfully.',
		status_code=status.HTTP_200_OK,
	)


@router.patch('/{course_id}/', response_model=ResponseData[CourseOut], status_code=status.HTTP_200_OK)
async def update_course(course_id: int, payload: CourseUpdate, db: DbSession):
	repo = CourseRepository(db)
	existing = repo.get(course_id)
	if not existing:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Course not found')
	obj = repo.update(course_id, payload.model_dump())
	return make_data_response(
		CourseOut.model_validate(obj, from_attributes=True),
		status_code=status.HTTP_200_OK,
		message='Course updated successfully',
	)


@router.delete('/{course_id}/', response_model=ResponseBase, status_code=status.HTTP_200_OK)
async def delete_course(course_id: int, db: DbSession):
	repo = CourseRepository(db)
	existing = repo.get(course_id)
	if not existing:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Course not found')
	repo.delete(course_id)
	return ResponseBase(
		success=True,
		status_code=status.HTTP_204_NO_CONTENT,
		message='Course deleted successfully.',
	)
