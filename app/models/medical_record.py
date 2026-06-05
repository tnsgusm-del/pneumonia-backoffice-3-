from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.models import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False)
    chart_number = Column(String(50), nullable=False)
    symptoms = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    patient = relationship("Patient", back_populates="medical_records")
    xray_images = relationship("XrayImage", back_populates="record")
    ai_analysis_results = relationship("AiAnalysisResult", back_populates="record")
