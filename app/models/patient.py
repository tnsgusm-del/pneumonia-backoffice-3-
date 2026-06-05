from sqlalchemy import Column, BigInteger, String, SmallInteger, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.models import Base
from app.models.user import GenderEnum


class Patient(Base):
    __tablename__ = "patients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, comment="환자 성명")
    age = Column(SmallInteger, nullable=False, comment="smallint")
    gender = Column(Enum(GenderEnum), nullable=True, comment="환자 성별")
    phone = Column(String(11), nullable=False, comment="환자 연락처, 국내 전화번호 기준")
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment="현재 시간")
    updated_at = Column(DateTime, nullable=True, onupdate=func.now(), comment="환자 정보 수정 일시")

    medical_records = relationship("MedicalRecord", back_populates="patient")
