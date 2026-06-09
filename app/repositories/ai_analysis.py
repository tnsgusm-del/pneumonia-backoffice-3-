from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ai_analysis_result import AiAnalysisResult


async def get_by_record_id(db: AsyncSession, record_id: int) -> AiAnalysisResult | None:
    result = await db.execute(
        select(AiAnalysisResult).where(AiAnalysisResult.record_id == record_id)
    )
    return result.scalars().first()


async def get_list_by_record_id(db: AsyncSession, record_id: int) -> list[AiAnalysisResult]:
    result = await db.execute(
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .order_by(AiAnalysisResult.created_at.desc())
    )
    return result.scalars().all()


async def create(
    db: AsyncSession,
    record_id: int,
    is_pneumonia: bool,
    confidence: float,
    heatmap_url: str | None,
    ai_model: str,
) -> AiAnalysisResult:
    analysis = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=is_pneumonia,
        confidence=confidence,
        heatmap_url=heatmap_url or "",
        ai_model=ai_model,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis
