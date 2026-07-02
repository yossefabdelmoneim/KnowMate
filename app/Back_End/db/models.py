from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.Back_End.db.session import Base


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True} # Added for consistency

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="company")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True} # Added to resolve the InvalidRequestError

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="employee")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="users")
    documents = relationship("Document", back_populates="user")
    # Updated relationship name to reflect the renamed ChatSession
    chat_sessions = relationship("LegacyChatSession", back_populates="user")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {'extend_existing': True} # Added for consistency

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(String(255), index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    doc_id = Column(String(255), unique=True, index=True, nullable=False)
    chunks = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="documents")


# Renamed ChatSession to LegacyChatSession to avoid conflict
class LegacyChatSession(Base):
    __tablename__ = "legacy_chat_sessions" # Renamed table
    __table_args__ = {'extend_existing': True} # Added for consistency

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = {'extend_existing': True} # Added for consistency

    id = Column(Integer, primary_key=True, index=True)
    # Updated ForeignKey to reference the renamed chat sessions table
    session_id = Column(Integer, ForeignKey("legacy_chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("LegacyChatSession", back_populates="messages")


class PendingCompanyRegistration(Base):
    __tablename__ = "pending_registrations"
    __table_args__ = {'extend_existing': True} # Added for consistency

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    admin_first_name = Column(String(255), nullable=False)
    admin_last_name = Column(String(255), nullable=False)
    admin_email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    verification_token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())