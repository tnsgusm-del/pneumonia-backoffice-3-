import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.models import Base


class GenderEnum(str, enum.Enum):
    M = "M"
    F = "F"


class RoleEnum(str, enum.Enum):
    PENDING = "PENDING"
    STAFF = "STAFF"
    ADMIN = "ADMIN"


class DepartmentEnum(str, enum.Enum):
    MEDICAL = "MEDICAL"
    DEV = "DEV"
    RESEARCH = "RESEARCH"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False, comment="평문 저장 x → 반드시 해싱")
    name = Column(String(20), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True, comment="유저 휴대폰 번호")
    gender = Column(Enum(GenderEnum), nullable=True, comment="성별 선택")
    department = Column(Enum(DepartmentEnum), nullable=True, comment="부서 선택")
    role = Column(Enum(RoleEnum), nullable=False, comment="부여된 역할 권한")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="현재 시간")
    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), comment="유저 정보 수정 일시")

    xray_images = relationship("XrayImage", back_populates="uploader")
