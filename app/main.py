from fastapi import FastAPI

from app.routers.company_routers import company_routers
from app.routers.user_routers import user_router
from app.core.config import settings
from app.core.middleware import setup_cors
import uvicorn
import logging


app = FastAPI()
setup_cors(app=app)
app.include_router(router=user_router)
app.include_router(router=company_routers)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
