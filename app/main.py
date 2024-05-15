from fastapi import FastAPI

from app.routers.company_routers import company_routers
from app.routers.invite_routers import invite_routers
from app.routers.quize_score_routers import results_router
from app.routers.user_routers import user_router
from app.core.config import settings
from app.core.middleware import setup_cors
import uvicorn
import logging


app = FastAPI()
setup_cors(app=app)

app.include_router(router=user_router)
app.include_router(router=company_routers)
app.include_router(router=invite_routers)
app.include_router(router=results_router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
