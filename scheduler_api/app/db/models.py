from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class LectureTypeEnum(str, enum.Enum):
    MATH = "math"
    PROGRAMMING = "programming"
    TECH_THEORY = "tech_theory"
    SOFT_SKILL = "soft_skill"

class TaskStatusEnum(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAIL = "fail"

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(SQLEnum(TaskStatusEnum), nullable=False, unique=True)
    
    tasks = relationship("Task", back_populates="task_status")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_status_id = Column(Integer, ForeignKey("task_statuses.id"), nullable=False)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=True)
    celery_task_id = Column(String, nullable=False)
    last_processing_timestamp = Column(DateTime, nullable=True)
    
    task_status = relationship("TaskStatus", back_populates="tasks")
    transcription = relationship("Transcription", back_populates="tasks")
    summary = relationship("Summary", back_populates="tasks")
    lectures = relationship("Lecture", back_populates="task")

class Lecture(Base):
    __tablename__ = "lectures"
    
    lecture_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lecture_recording_path = Column(String, nullable=False)
    lecture_type = Column(SQLEnum(LectureTypeEnum), nullable=False)
    is_processed = Column(Boolean, nullable=False, server_default='false')
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    task = relationship("Task", back_populates="lectures")

class Prompt(Base):
    __tablename__ = "prompts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    type = Column(String, nullable=False)
    prompt_text = Column(Text, nullable=False)

class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    summary_text = Column(Text, nullable=False)
    last_processing_timestamp = Column(DateTime, nullable=True)
    
    tasks = relationship("Task", back_populates="summary")

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transcription_text = Column(Text, nullable=False)
    
    tasks = relationship("Task", back_populates="transcription")