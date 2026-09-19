import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///:memory:" if os.environ.get("TESTING") else "sqlite:///./dca_data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# We need to import all models here so metadata knows about them before create_all
class DBActiveLearningConfig(Base):
    __tablename__ = "active_learning_configs"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    strategy = Column(String, default="uncertainty")
    batch_size = Column(Integer, default=10)
    is_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBActiveLearningRound(Base):
    __tablename__ = "al_rounds"
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, index=True)
    round_number = Column(Integer)
    selected_tasks = Column(JSON) # List of ints
    task_count = Column(Integer)
    strategy_used = Column(String)
    avg_uncertainty = Column(Float, nullable=True)
    diversity_score = Column(Float, nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBDriftBaseline(Base):
    __tablename__ = "drift_baselines"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    name = Column(String)
    feature_statistics = Column(JSON)
    label_distribution = Column(JSON)
    sample_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class DBQualityReport(Base):
    __tablename__ = "quality_reports"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    overall_score = Column(Float)
    consistency_score = Column(Float)
    agreement_score = Column(Float)
    completeness_score = Column(Float)
    issue_count = Column(Integer)
    issues = Column(JSON) # serialized issues
    created_at = Column(DateTime, default=datetime.utcnow)

class DBVersionCommit(Base):
    __tablename__ = "version_commits"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    version_id = Column(String, index=True)
    data_hash = Column(String)
    description = Column(String)
    parent_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)
