from fastapi import FastAPI
from app.routers.routers import router
from app.core.config import settings
import uvicorn

app = FastAPI()

app.include_router(router=router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)
