import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Date, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 10})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    status = Column(String(20), default="pending")  # pending / active / disabled
    is_admin = Column(Integer, default=0)
    session_version = Column(Integer, default=0)
    last_login_at = Column(DateTime)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_study_date = Column(Date)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    progress = relationship("UserProgress", back_populates="user", lazy="dynamic")
    chunks = relationship("UserChunk", back_populates="user", lazy="dynamic")
    chat_logs = relationship("ChatLog", back_populates="user", lazy="dynamic")


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    title_cn = Column(String(200))
    category = Column(String(200))
    dialogue_script = Column(JSON)
    chunks = Column(JSON)
    pattern_focus = Column(Text)
    reaction_questions = Column(JSON)
    can_do = Column(String(500))
    audio_dialogue = Column(String(500))
    audio_chunks = Column(JSON)


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), index=True)
    step1_done = Column(Integer, default=0)
    step2_done = Column(Integer, default=0)
    step3_done = Column(Integer, default=0)
    step4_done = Column(Integer, default=0)
    step5_done = Column(Integer, default=0)
    step6_done = Column(Integer, default=0)
    completed_at = Column(DateTime, index=True)
    can_do_self_eval = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "scenario_id", name="uq_user_scenario"),
    )
    user = relationship("User", back_populates="progress")


class UserChunk(Base):
    __tablename__ = "user_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    chunk_text = Column(String(500))
    translation = Column(String(500))
    scene_sentence = Column(Text)
    mastery = Column(Integer, default=1)  # 1=遗忘 2=需复习 3=熟练
    next_review_at = Column(DateTime)
    collected_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_reviewed_at = Column(DateTime)

    __table_args__ = (
        Index("idx_userchunk_user_review", "user_id", "next_review_at"),
    )
    user = relationship("User", back_populates="chunks")


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"))
    role = Column(String(20))
    content = Column(Text)
    tip = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_chatlog_user_scenario", "user_id", "scenario_id", "created_at"),
    )
    user = relationship("User", back_populates="chat_logs")


def init_db():
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), exist_ok=True)
    Base.metadata.create_all(bind=engine)
    # Enable WAL mode for concurrent read/write
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA journal_mode=WAL;")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
