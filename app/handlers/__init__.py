from app.handlers.start import router as start_router
from app.handlers.catalog import router as catalog_router
from app.handlers.order import router as order_router
from app.handlers.questions import router as questions_router
from app.handlers.common import router as common_router

__all__ = [
    "start_router",
    "catalog_router",
    "order_router",
    "questions_router",
    "common_router",
]
