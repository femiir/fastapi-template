from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status as http_status

from api import course_router, newsletter_router, track_router, module_router
from config.settings import settings
from db.conf import db_health, engine, init_db
from schemas import make_response


@asynccontextmanager
async def lifespan(app: FastAPI):
	with engine.connect() as conn:
		conn.exec_driver_sql('SELECT 1')
	if getattr(settings, 'debug', False):
		init_db()
	yield
	engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(newsletter_router)
app.include_router(track_router)
app.include_router(course_router)
app.include_router(module_router)


# ---- Global exception handlers ----
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(
		status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
		content=make_response(
			status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
			success=False,
			message=exc.errors(),
		).model_dump(),
	)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
	# You might log exc here.
	return JSONResponse(
		status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
		content=make_response(
			status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
			success=False,
			message=str(exc),
		).model_dump(),
	)


@app.get('/info', tags=['Info'])
async def info():
	return {'app_name': settings.app_name, 'database_status': db_health()}
