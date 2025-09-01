from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from config.settings import settings

DATABASE_URL = settings.database_url

if DATABASE_URL:
	# Single engine
	engine = create_engine(
		str(DATABASE_URL),
		echo=getattr(settings, 'debug', False),
		pool_pre_ping=True,
		pool_size=10,
		max_overflow=20,
	)
else:
	raise NotImplementedError('Database URL not found')

# Factory to build sessions with consistent defaults
SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
	class_=Session,
	expire_on_commit=False,  # keep objects usable after commit (common for APIs)
)


def init_db() -> None:
	import models  # noqa: F401

	print('Creating database tables...')
	SQLModel.metadata.create_all(engine)
	# print('Tables now:', list(SQLModel.metadata.tables.keys()))


def db_health():
	with engine.connect() as conn:
		conn.exec_driver_sql('SELECT 1')
	return {'status': 'ok'}
