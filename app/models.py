from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Column, Integer, String, Text, Float , ForeignKey

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_text = Column(Text)
    analysis_result = Column(Text)

    user = relationship("User")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    questions = Column(Text)
    answers = Column(Text)
    evaluation = Column(Text)

class AgentMemory(Base):
    __tablename__ = "agent_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    memory_type = Column(Text)   # weakness / strength / goal
    content = Column(Text)


class SkillScore(Base):
    __tablename__ = "skill_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skill_name = Column(String)
    score = Column(Float)
