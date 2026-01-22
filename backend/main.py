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
from backend.auth.google_auth import router as google_auth_router 
from backend.plans.plans_routes import router as plans_router
from backend.users.user_routes import router as user_router
from backend.auth.google_oauth_routes import router as google_oauth_router
from backend.calendar.calendar_routes import router as calendar_router




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
    allow_origins=[
        "http://localhost:3000",
        "https://neuroflow-os.vercel.app"],
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
app.include_router(google_auth_router)
app.include_router(plans_router)
app.include_router(user_router)
app.include_router(google_oauth_router)
app.include_router(calendar_router)
















































