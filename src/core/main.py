from fastapi import FastAPI
from config.settings import settings
from contextlib import asynccontextmanager
from src.db.conf import engine, init_db, db_health  
@asynccontextmanager
async def lifespan(app: FastAPI):
	
	with engine.connect() as conn:
		conn.exec_driver_sql('SELECT 1')
	if getattr(settings, 'debug', False):
		init_db()
	yield
	engine.dispose()


app = FastAPI(lifespan=lifespan)

# Routers
from api.news.newsletter_router import router as newsletter_router  # noqa: E402

app.include_router(newsletter_router)


@app.get('/')
async def root():
	return {'message': 'Hello Worlder!'}


@app.get('/info')
async def info():
	return {'app_name': settings.app_name, 'database_status': db_health()}
