import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.db.session import engine
from app.models.user import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("DEV_CREATE_TABLES", "false").lower() == "true":
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title="Evaluación 2 - Login API", lifespan=lifespan)

# El frontend local usa proxy de Vite; dominios externos se configuran explícitamente.
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["POST"], allow_headers=["Content-Type"])
app.include_router(auth_router)

@app.get("/health", tags=["Operación"])
async def health():
    return {"status": "ok"}
