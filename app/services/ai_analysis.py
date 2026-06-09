from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select

from app.models.ai_analysis_result import AiAnalysisResult
from app.models.medical_record import MedicalRecord
from app.repositories import ai_analysis as ai_repo
from worker.model import predict

AI_MODEL_NAME = "EfficientNet-B4+B3-Ensemble"


async def predict_or_get(db: AsyncSession, record_id: int) -> tuple[AiAnalysisResult, bool]:
    result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.id == record_id)
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="해당 진료기록을 찾을 수 없습니다.")

    existing = await ai_repo.get_by_record_id(db, record_id)
    if existing:
        return existing, False

    try:
        prediction = predict(record.xray_image_path)
    except Exception:
        raise HTTPException(status_code=500, detail="AI 예측 중 오류가 발생했습니다.")

    analysis = await ai_repo.create(
        db=db,
        record_id=record_id,
        is_pneumonia=prediction["is_pneumonia"],
        confidence=prediction["confidence"],
        heatmap_url=None,
        ai_model=AI_MODEL_NAME,
    )
    return analysis, True


async def get_list(db: AsyncSession, record_id: int) -> list[AiAnalysisResult]:
    result = await db.execute(
        select(MedicalRecord).where(MedicalRecord.id == record_id)
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="해당 진료기록을 찾을 수 없습니다.")

    return await ai_repo.get_list_by_record_id(db, record_id)
