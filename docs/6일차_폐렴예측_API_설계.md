# 6일차 과제: AI 폐렴 예측 및 결과 조회 API 설계 명세서

본 문서는 AI 폐렴 예측 및 결과 조회 요구사항 정의서(`REQ-PRED-001` ~ `NFR-PRED-002`)에 기반하여 설계된 최종 RESTful API 명세서입니다.
5일차에 업로드된 환자의 흉부 X-ray 이미지 데이터를 `worker/model.py`에 로드된 PyTorch `SimpleCNN` 싱글톤 모델과 안전하게 연동하여 실시간으로 폐렴 분석을 구동하고 연산 결과를 시스템에 기록하는 아키텍처를 가집니다.

---

## 🗺️ API 요약 가이드

| 요구사항 ID | 기능 요약 | Method | Endpoint | 권한 |
| :--- | :--- | :---: | :--- | :--- |
| **REQ-PRED-001** | AI 모델 활용 폐렴 예측 수행 및 저장 | `POST` | `/api/v1/ai-analysis/{record_id}` | 의료인 (`STAFF`, `ADMIN`) |
| **REQ-PRED-002** | AI 모델 활용 폐렴 예측 결과 상세 조회 | `GET` | `/api/v1/ai-analysis/records/{record_id}` | 로그인 유저 전체 |

---

## ⚡ 비기능 요구사항 (Non-Functional Requirements)

| ID | 요구사항 내용 | 적용 방식 |
| :--- | :--- | :--- |
| **NFR-PRED-001** | 모든 AI 관련 API는 최대 3초 이내에 로직을 처리하고 응답하도록 한다. (실시간 추론 속도 보장) | PyTorch `torch.no_grad()` 메모리 제어 및 글로벌 모델 싱글톤 캐싱 기법 적용 |

---

## 📑 상세 API 명세

### REQ-PRED-001. 실시간 AI 폐렴 분석 및 저장 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | 실시간 AI 폐렴 분석 및 결과 기록 API |
| **설명** | 지정된 진료기록 고유 ID의 X-ray 이미지를 탐색하여 AI 모델로 폐렴 여부를 분석하고 결과를 데이터베이스에 저장함 |
| **엔드포인트** | `/api/v1/ai-analysis/{record_id}` |
| **메서드** | `POST` |
| **인증 필요** | Y (의료인 권한: `STAFF` / `ADMIN`) |

#### 2. 요청 (Request)

* **Headers**
  * `Authorization: Bearer <access_token>`

* **패스 파라미터 (Path Parameters)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **record_id** | integer | Y | 분석을 실행할 진료 기록의 고유 식별자 |

#### 3. 응답 (Response)

* **성공 (201 Created)**: 분석이 완료되어 데이터베이스 적재에 성공한 상황

```json
{
  "id": 5,
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 92.45,
  "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
  "ai_model": "SimpleCNN_v1",
  "created_at": "2026-06-10T16:45:12"
}
```

* **성공 (200 OK)**: 중복 분석 방지 가동 시, 이미 완료된 기존 분석 결과를 즉시 반환

```json
{
  "id": 5,
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 92.45,
  "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
  "ai_model": "SimpleCNN_v1",
  "created_at": "2026-06-10T16:45:12"
}
```

* **실패 (404 Not Found - 진료기록 없음)**

```json
{
  "detail": "지정한 진료기록(ID: 999)이 존재하지 않습니다."
}
```

* **실패 (400 Bad Request - X-ray 누락)**

```json
{
  "detail": "해당 진료기록에 첨부된 흉부 X-ray 이미지 파일이 존재하지 않아 분석을 진행할 수 없습니다."
}
```

#### 4. 비고

* 동일 모델명으로 이미 저장된 결과가 존재한다면 추가 추론 연산을 발생시키지 않고 데이터베이스 캐시를 즉시 응답하는 중복 분석 방지 캐싱 로직이 설계되어 있습니다.

---

### REQ-PRED-002. 특정 진료기록의 AI 분석 결과 조회 API

#### 1. API 개요

| 항목 | 내용 |
| :--- | :--- |
| **API 이름** | AI 분석 결과 상세 조회 API |
| **설명** | 특정 진료 기록에 대해 완료된 AI 예측 결과 및 판별 확률 값을 조회함 |
| **엔드포인트** | `/api/v1/ai-analysis/records/{record_id}` |
| **메서드** | `GET` |
| **인증 필요** | Y |

#### 2. 요청 (Request)

* **Headers**
  * `Authorization: Bearer <access_token>`

* **패스 파라미터 (Path Parameters)**

| 파라미터명 | 타입 | 필수 여부 | 설명 |
| :--- | :--- | :---: | :--- |
| **record_id** | integer | Y | 판독 결과를 조회할 진료 기록의 고유 식별자 |

#### 3. 응답 (Response)

* **성공 (200 OK)**

```json
{
  "id": 5,
  "record_id": 1,
  "is_pneumonia": true,
  "confidence": 92.45,
  "heatmap_url": "/media/xray/heatmap_c354a708-1370-40e8-9da2.jpg",
  "ai_model": "SimpleCNN_v1",
  "created_at": "2026-06-10T16:45:12"
}
```

* **실패 (404 Not Found)**

```json
{
  "detail": "해당 진료기록에 대해 가동된 AI 판독 이력이 존재하지 않습니다."
}
```
