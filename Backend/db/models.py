from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Null for Google OAuth users
    is_google_user = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    templates = relationship("Template", back_populates="user", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="user", cascade="all, delete-orphan")

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # Store as JSON array
    attachment_path = Column(String(500), nullable=True)
    attachment_name = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="templates")
    email_logs = relationship("EmailLog", back_populates="template")

class EmailLog(Base):
    __tablename__ = 'email_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey('templates.id'), nullable=True, index=True)  # Made nullable
    recipient_email = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # sent, failed, pending
    error_message = Column(Text, nullable=True)
    gmail_message_id = Column(String(255), nullable=True)
    sent_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="email_logs")
    template = relationship("Template", back_populates="email_logs")
