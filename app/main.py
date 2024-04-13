from fastapi import FastAPI
from app.routers.routers import router
from app.core.config import settings
from app.core.middleware import setup_cors
import uvicorn
import logging

app = FastAPI()
setup_cors(app=app)
app.include_router(router=router)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
