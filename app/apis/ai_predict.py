from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db as get_db
from app.schemas.ai_analysis import AiAnalysisResultResponse
from app.services import ai_analysis as ai_service

router = APIRouter(prefix="/api/v1/medical-records", tags=["AI Predict"])


@router.post(
    "/{record_id}/ai-predict",
    summary="폐렴 AI 예측",
    description="진료기록의 X-Ray 이미지로 폐렴을 예측합니다. 기존 결과가 있으면 재사용합니다.",
)
async def predict_pneumonia(
    record_id: int,
    db: AsyncSession = Depends(get_db),
):
    analysis, is_new = await ai_service.predict_or_get(db, record_id)

    from fastapi.responses import JSONResponse
    from fastapi import status

    status_code = status.HTTP_201_CREATED if is_new else status.HTTP_200_OK
    return JSONResponse(
        status_code=status_code,
        content=AiAnalysisResultResponse.model_validate(analysis).model_dump(mode="json"),
    )


@router.get(
    "/{record_id}/ai-predict",
    response_model=list[AiAnalysisResultResponse],
    summary="폐렴 AI 예측 결과 목록 조회",
    description="특정 진료기록의 AI 예측 결과 목록을 조회합니다.",
)
async def get_predict_list(
    record_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await ai_service.get_list(db, record_id)
