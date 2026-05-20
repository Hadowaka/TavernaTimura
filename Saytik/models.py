from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import datetime

# SQLite database file (creates forum.db in the same folder)
DATABASE_URL = "sqlite:///./forum.db"

# Engine is the core interface to the database.
# connect_args={"check_same_thread": False} is needed for SQLite to work with FastAPI's thread pool.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal is a factory for new database sessions.
# Each request will get its own session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models.
Base = declarative_base()

# ---------- Model definitions ----------

class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship: a thread can have many posts.
    # cascade="all, delete-orphan" means deleting a thread also deletes its posts.
    posts = relationship("Post", back_populates="thread", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign key linking each post to one thread.
    thread_id = Column(Integer, ForeignKey("threads.id"))

    # Back-reference so a post knows its parent thread.
    thread = relationship("Thread", back_populates="posts")


# Create all tables in the database (if they don't exist yet).
Base.metadata.create_all(bind=engine)
