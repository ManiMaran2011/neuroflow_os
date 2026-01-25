from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


# ------------------------
# USER MODEL
# ------------------------
class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    xp = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
# ------------------------
# GOOGLE OAUTH TOKEN MODEL
# ------------------------
class GoogleOAuthToken(Base):
    __tablename__ = "google_oauth_tokens"

    user_email = Column(String, primary_key=True, index=True)

    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)

    scope = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------
# EXECUTION MODEL
# ------------------------
class Execution(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_email = Column(String, index=True)

    intent = Column(String)
    actions = Column(JSON)
    agents = Column(JSON)
    params = Column(JSON)

    status = Column(String, default="created")
    requires_approval = Column(Boolean, default=False)

    # ✅ COST TRACKING
    estimated_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)

    # ✅ XP PER EXECUTION (NEW)
    xp_gained = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------
# EXECUTION TIMELINE
# ------------------------
class ExecutionTimeline(Base):
    __tablename__ = "execution_timeline"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String, index=True)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# ------------------------
# USER STREAK MODEL
# ------------------------
class UserStreak(Base):
    __tablename__ = "user_streaks"

    user_email = Column(String, primary_key=True, index=True)
    current_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime, nullable=True)








