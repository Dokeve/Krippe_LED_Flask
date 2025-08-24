from sqlalchemy import create_engine, Integer, String, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from datetime import datetime
from config import Config
engine=create_engine(Config.db_uri(), pool_pre_ping=True, echo=False, future=True)
SessionLocal=sessionmaker(bind=engine, expire_on_commit=False)
class Base(DeclarativeBase): pass
class Group(Base):
    __tablename__='groups'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(120), unique=True)
    led_indices: Mapped[str]=mapped_column(Text, default='')
    color: Mapped[str]=mapped_column(String(7), default='#FFFFFF')
class CalendarEntry(Base):
    __tablename__='calendar'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    start: Mapped[datetime]=mapped_column(DateTime)
    end: Mapped[datetime]=mapped_column(DateTime)
    mode: Mapped[int]=mapped_column(Integer, default=0)
    color: Mapped[str]=mapped_column(String(7), default='#FFFFFF')
class AudioPhase(Base):
    __tablename__='audio_phases'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    phase: Mapped[str]=mapped_column(String(20), unique=True)
    file_path: Mapped[str]=mapped_column(String(255))
class Announcement(Base):
    __tablename__='announcements'
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(120))
    start: Mapped[datetime]=mapped_column(DateTime)
    end: Mapped[datetime]=mapped_column(DateTime)
    file_path: Mapped[str]=mapped_column(String(255))
    volume: Mapped[int]=mapped_column(Integer, default=100)

def init_db():
    Base.metadata.create_all(bind=engine)
