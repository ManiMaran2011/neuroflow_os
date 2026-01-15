from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import engine
from backend.db.models import Base

from backend.auth.auth_routes import router as auth_router
from backend.ask_routes import router as ask_router
from backend.execution.execution_routes import router as execution_router
from backend.voice.voice_routes import router as voice_router


# -------------------------
# CREATE APP
# -------------------------
app = FastAPI()


# -------------------------
# CREATE DATABASE TABLES ✅
# -------------------------
Base.metadata.create_all(bind=engine)


# -------------------------
# CORS
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# ROUTES
# -------------------------
app.include_router(auth_router)
app.include_router(ask_router)
app.include_router(execution_router)
app.include_router(voice_router)














































