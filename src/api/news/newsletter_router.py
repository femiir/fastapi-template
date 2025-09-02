from fastapi import APIRouter, HTTPException, status

from dependencies import DbSession, Pagination
from repositories import NewsletterRepository
from schemas import PageMeta, Paginated, ResponseBase, ResponseData, make_data_response, make_response
from schemas.news import SubscribeIn, SubscriberOut, Unsubscribe

router = APIRouter(prefix='/newsletter', tags=['Newsletter'])


@router.post('/subscribe', response_model=ResponseData[SubscriberOut], status_code=status.HTTP_201_CREATED)
async def subscribe(subscriber: SubscribeIn, db: DbSession):
	repo = NewsletterRepository(db)
	existing = repo.get_by_email(subscriber.email, include_deleted=True)
	if existing:
		if not existing.is_active:
			repo.restore(subscriber.email)
			existing = repo.get_by_email(subscriber.email)
			out_obj = SubscriberOut.model_validate(existing, from_attributes=True)
			return make_data_response(
				out_obj,
				status_code=status.HTTP_200_OK,
				message='Subscriber restored successfully.',
			)
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail='Email already subscribed.',
		)
	new_subscriber = repo.create(subscriber.email)
	out_obj = SubscriberOut.model_validate(new_subscriber, from_attributes=True)
	return make_data_response(
		out_obj, status_code=status.HTTP_201_CREATED, message='Subscriber created successfully.'
	)


@router.get('/subscribers', response_model=Paginated[SubscriberOut], status_code=status.HTTP_200_OK)
async def list_subscribers(pagination: Pagination, db: DbSession):
	repo = NewsletterRepository(db)
	raw_items = repo.get_all(limit=pagination.limit, offset=pagination.offset)
	items = [SubscriberOut.model_validate(obj, from_attributes=True) for obj in raw_items]
	total = repo.count()
	pages = (total // pagination.limit + (1 if total % pagination.limit else 0)) if pagination.limit else None
	meta = PageMeta(
		total=total,
		limit=pagination.limit,
		offset=pagination.offset,
		pages=pages,
	)
	return Paginated[SubscriberOut](
		success=True,
		status_code=status.HTTP_200_OK,
		message='Subscribers retrieved successfully.',
		meta=meta,
		items=items,
	)


@router.delete('/unsubscribe', response_model=ResponseBase, status_code=status.HTTP_200_OK)
async def unsubscribe(unsubscriber: Unsubscribe, db: DbSession):
	repo = NewsletterRepository(db)
	existing = repo.get_by_public_id(unsubscriber.public_id)
	if not existing:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail='Subscriber not found.',
		)
	repo.soft_delete(unsubscriber.public_id)
	return make_response(
		status_code=status.HTTP_204_NO_CONTENT, success=True, message='Subscriber unsubscribed successfully.'
	)
