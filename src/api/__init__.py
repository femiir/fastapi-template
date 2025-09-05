from .news.newsletter_router import router as newsletter_router
from .tracks.course_router import router as course_router
from .tracks.module_router import router as module_router
from .tracks.track_router import router as track_router

__all__ = ['course_router', 'module_router', 'newsletter_router', 'track_router']
