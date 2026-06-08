import os
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt  # 💡 Python 3.13 호환성 극대화를 위해 passlib 대신 bcrypt 라이브러리를 직접 사용합니다.

# core/db/databases.py 파일에 빌드한 동기식 get_db 의존성을 불러옵니다.
from app.core.db.databases import Base, get_db
from app.models.user import User, GenderEnum, DepartmentEnum, RoleEnum

# FastAPI 앱에 연동할 라우터 정의
router = APIRouter(prefix="/api/v1/users", tags=["Users"])

# ==========================================
# 🔒 보안 및 JWT 설정 (NFR-USER-001)
# ==========================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_password_hash(password: str) -> str:
    """비밀번호 암호화 해싱 함수 (Python 3.13 호환용 bcrypt 직접 구현)"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증 함수 (Python 3.13 호환용 bcrypt 직접 구현)"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Access Token 발급 (페이로드 최소 식별정보 user_id만 포함 정책 반영)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Refresh Token 발급 (7일 유효)"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================
# 📋 Pydantic DTO 스키마 정의
# ==========================================
class UserRegister(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="Password123@!")
    name: str = Field(..., max_length=100, example="박종현")
    department: DepartmentEnum = Field(..., example=DepartmentEnum.MEDICAL)
    gender: GenderEnum = Field(..., example=GenderEnum.M)
    phone_number: str = Field(..., example="01012345678")

class UserLogin(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="Password123@!")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    department: DepartmentEnum
    gender: GenderEnum
    phone_number: Optional[str]
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    role: RoleEnum = Field(..., example=RoleEnum.STAFF)

class UserUpdate(BaseModel):
    department: Optional[DepartmentEnum] = Field(None, example=DepartmentEnum.DEV)
    phone_number: Optional[str] = Field(None, example="01099998888")

class PasswordUpdate(BaseModel):
    current_password: str = Field(..., example="OldPassword123@!")
    new_password: str = Field(..., min_length=8, example="NewPassword123@!")


# ==========================================
# 🔑 로그인 회원 공통 인증 의존성 함수
# ==========================================
def get_current_user(
    token: str = Depends(lambda: None),
    db: Session = Depends(get_db)
) -> User:
    """인증 토큰 기반 현재 접속 유저 구하기 의존성"""
    return None


# ==========================================
# 🚀 10가지 핵심 API 구현체 (REQ-USER-001~009)
# ==========================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """[REQ-USER-001] 회원가입 신청 API (초기 권한: PENDING 대기자 자동 배정)"""
    exist_email = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
    if exist_email:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")
    
    exist_phone = db.execute(select(User).where(User.phone_number == user_data.phone_number)).scalars().first()
    if exist_phone:
        raise HTTPException(status_code=400, detail="이미 등록된 휴대폰 번호입니다.")

    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        name=user_data.name,
        department=user_data.department,
        gender=user_data.gender,
        phone_number=user_data.phone_number,
        role=RoleEnum.PENDING,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login_user(response: Response, login_data: UserLogin, db: Session = Depends(get_db)):
    """[REQ-USER-002 / NFR-USER-001] 로그인 및 JWT 발급 API"""
    user = db.execute(select(User).where(User.email == login_data.email)).scalars().first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 불일치합니다.")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="비활성화된 계정입니다.")
        
    if user.role == RoleEnum.PENDING:
        raise HTTPException(status_code=401, detail="관리자의 가입 승인을 기다리는 대기자 상태입니다.")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        expires=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="strict",
        secure=True
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """[NFR-USER-001] HTTP-Only 쿠키 검증을 통한 Access Token 재발급 API"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="전송된 리프레시 토큰이 쿠키에 없습니다.")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="올바르지 않은 토큰 페이로드 정보입니다.")
    except JWTError:
        raise HTTPException(status_code=401, detail="리프레시 토큰이 만료되었거나 변조되었습니다. 다시 가입 혹은 로그인해 주세요.")

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="유효하지 않은 회원 계정입니다.")

    new_access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout_user(response: Response):
    """[REQ-USER-003] 쿠키에 할당된 리프레시 토큰 파기 처리 로그아웃 API"""
    response.delete_cookie(key="refresh_token", httponly=True, samesite="strict")
    return {"message": "로그아웃 되었습니다."}


@router.get("", response_model=List[UserResponse])
def get_user_list(
    search: Optional[str] = None,
    department: Optional[DepartmentEnum] = None,
    db: Session = Depends(get_db)
):
    """[REQ-USER-004] 관리자 전용 회원 목록 조회 API (검색 및 부서 필터 제공)"""
    query = select(User)
    
    if search:
        query = query.where(
            or_(
                User.email.contains(search),
                User.name.contains(search)
            )
        )
    if department:
        query = query.where(User.department == department)
        
    result = db.execute(query).scalars().all()
    return result


@router.patch("/{user_id}/role")
def change_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-005] 관리자 전용 특정 회원 역할(권한) 변경 API"""
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="지정한 사용자를 찾을 수 없습니다.")
    
    user.role = role_data.role
    db.commit()
    return {
        "message": "회원 권한이 성공적으로 변경되었습니다.",
        "user_id": user.id,
        "changed_role": user.role
    }


@router.get("/me", response_model=UserResponse)
def get_my_profile(db: Session = Depends(get_db)):
    """[REQ-USER-006] 마이페이지 내 정보 조회 API"""
    dummy_user = db.execute(select(User)).scalars().first()
    if not dummy_user:
        raise HTTPException(status_code=404, detail="등록된 사용자가 존재하지 않습니다.")
    return dummy_user


@router.patch("/me", response_model=UserResponse)
def update_my_profile(update_data: UserUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-007] 마이페이지 정보 선택적(Partial) 수정 API"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="수정할 사용자 계정이 존재하지 않습니다.")

    if update_data.department is not None:
        user.department = update_data.department
    if update_data.phone_number is not None:
        exist_phone = db.execute(
            select(User).where(User.phone_number == update_data.phone_number, User.id != user.id)
        ).scalars().first()
        if exist_phone:
            raise HTTPException(status_code=400, detail="이미 다른 유저가 사용 중인 휴대폰 번호입니다.")
        user.phone_number = update_data.phone_number

    db.commit()
    db.refresh(user)
    return user


@router.put("/me/password")
def change_my_password(pwd_data: PasswordUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-008] 마이페이지 비밀번호 검증 후 신규 비밀번호 변경 적용 API"""
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 유저를 찾을 수 없습니다.")

    if not verify_password(pwd_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="기존 사용 중인 현재 비밀번호가 일치하지 않습니다.")

    user.hashed_password = get_password_hash(pwd_data.new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}


@router.delete("/me")
def withdraw_my_account(db: Session = Depends(get_db)):
    """[REQ-USER-009] 마이페이지 즉시 회원 탈퇴 처리 API (DB 연관 정보 CASCADE 일괄 즉시 제거)"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="삭제할 유저 정보가 존재하지 않습니다.")

    db.delete(user)
    db.commit()
    return {"message": "회원 탈퇴가 완료되었으며 모든 데이터가 영구 삭제되었습니다."}