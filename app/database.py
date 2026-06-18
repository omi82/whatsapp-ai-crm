from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# DATABASE URL
# =========================================================

# The DATABASE_URL environment variable should be set in the .env file.
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# DATABASE ENGINE
# =========================================================

engine = create_engine(
    DATABASE_URL
)

# =========================================================
# SESSION LOCAL
# =========================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# =========================================================
# BASE CLASS
# =========================================================

Base = declarative_base()

# =========================================================
# CHAT HISTORY TABLE
# =========================================================

class ChatHistory(Base):

    __tablename__ = "chat_history"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # NEW CHANGE
    # SESSION ID FOR CONVERSATIONAL MEMORY
    # =====================================================
    #
    # WHY ADDED?
    #
    # This helps identify unique users/conversations.
    #
    # Example:
    # user_101
    # whatsapp_9876543210
    #
    # All chats from same session_id
    # become part of same conversation memory.
    #
    # =====================================================

    session_id = Column(
        String,
        nullable=False,
        index=True
    )

    user_name = Column(
        String,
        nullable=True
    )

    # =====================================================
    # USER MESSAGE
    # =====================================================

    user_message = Column(
        String,
        nullable=False
    )

    # =====================================================
    # AI REPLY
    # =====================================================

    ai_reply = Column(
        String,
        nullable=False
    )

    # =====================================================
    # CREATED TIME
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# =========================================================
# ChatHistory  
# =========================================================

class Customer(Base):

    __tablename__ = "customers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # WhatsApp Number
    phone = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    # Lead Qualification Fields
    name = Column(String, nullable=True)

    gender = Column(String, nullable=True)

    age = Column(Integer, nullable=True)

    city = Column(String, nullable=True)

    service = Column(String, nullable=True)

    requirement = Column(String, nullable=True)

    budget = Column(String, nullable=True)

    summary = Column(String, nullable=True)

    # Current Conversation Stage
    stage = Column(
        String,
        default="name",
        nullable=False
    )

    # Lead Status
    status = Column(
        String,
        default="new"
    )

    # Created Time
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================================================
# USERS TABLE
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        nullable=False,
        default="viewer"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(bind=engine)

# =========================================================
# DATABASE SESSION DEPENDENCY
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



