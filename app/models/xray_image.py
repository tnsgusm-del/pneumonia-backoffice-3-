from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.models import Base


class XrayImage(Base):
    __tablename__ = "xray_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    record_id = Column(BigInteger, ForeignKey("medical_records.id"), nullable=False)
    uploader_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(2048), nullable=False)
    shooting_datetime = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    record = relationship("MedicalRecord", back_populates="xray_images")
    uploader = relationship("User", back_populates="xray_images")
    ai_analysis_results = relationship("AiAnalysisResult", back_populates="xray_image")
