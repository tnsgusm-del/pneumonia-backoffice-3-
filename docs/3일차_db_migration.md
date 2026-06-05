# 3일차 DB Migration

## 1. 모델 파일 구조

```
app/models/
├── user.py              # users 테이블 (GenderEnum, RoleEnum, DepartmentEnum 포함)
├── patient.py           # patients 테이블
├── medical_record.py    # medical_records 테이블
├── xray_image.py        # xray_images 테이블
└── ai_analysis_result.py # ai_analysis_results 테이블
```

## 2. Alembic 마이그레이션 수행 방법

### 환경 설정

`alembic/env.py`에서 모델 import 및 DB URL 설정:

```python
from app.core.config import settings
from app.core.db.models import Base

# 모든 모델 import (autogenerate 감지를 위해 필수)
from app.models import user, patient, medical_record, xray_image, ai_analysis_result

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

### 마이그레이션 명령어

```bash
# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "create initial tables"

# DB에 적용
alembic upgrade head

# 현재 상태 확인
alembic current

# 롤백
alembic downgrade -1
```

## 3. DB 스키마 적용 확인

> DB Viewer(DBeaver, TablePlus 등)로 확인한 스키마 캡처 이미지를 아래에 첨부합니다.

<!-- 이미지 첨부 -->
![DB Schema](./images/db_schema.png)
