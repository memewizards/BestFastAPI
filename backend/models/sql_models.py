from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    
    username = Column(String, primary_key=True)
    password = Column(String)
    badges = Column(postgresql.ARRAY(String), default=[])
    role = Column(String, default="freelancer")  # 'admin', 'client', 'freelancer'
    reputation = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    email = Column(String, unique=True, nullable=True)
    wallet_address = Column(String, nullable=True)
    user_rank = Column(String, default="beginner")  # Renamed from rank
    profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Field to indicate whether the user's email is verified
    email_is_verified = Column(Boolean, default=False)
    
    # Verification token used during sign-up; cleared upon email verification
    verification_token = Column(String, nullable=True)


class DBPasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    token = Column(String, unique=True, index=True)
    expires = Column(DateTime)