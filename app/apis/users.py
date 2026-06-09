import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt

from app.core.db.databases import Base, get_db
from app.models.user import User, GenderEnum, DepartmentEnum, RoleEnum

# ==========================================
# 🗺️ APIRouter ñemoambue (Mbohovái 1, 2)
# ==========================================
# Auth router (/api/v1/auth)
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

# User router (/api/v1/users)
user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# ==========================================
# 🔒 Ñangareko ha JWT ñemboheko (NFR-USER-001)
# ==========================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def get_password_hash(password: str) -> str:
    """Tembiapo ñe'ẽñemi ñemoambue hag̃ua"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Tembiapo ñe'ẽñemi ñeha'arõ hag̃ua"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Mba'e ome'ẽva Access Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Mba'e ome'ẽva Refresh Token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==========================================
# 📋 Pydantic DTO ñemboheko (Mbohovái 4, 5)
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
# 🚀 Auth Router kuatia (/api/v1/auth)
# ==========================================

@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """[REQ-USER-001] User mbohapypyry pyahu"""
    exist_email = db.execute(select(User).where(User.email == user_data.email)).scalars().first()
    if exist_email:
        raise HTTPException(status_code=400, detail="Ko e-mail oĩma ñandutípe.")
    
    exist_phone = db.execute(select(User).where(User.phone_number == user_data.phone_number)).scalars().first()
    if exist_phone:
        raise HTTPException(status_code=400, detail="Ko pumbyry papapy oĩma mbohapypyry.")

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


@auth_router.post("/login", response_model=TokenResponse)
def login_user(response: Response, login_data: UserLogin, db: Session = Depends(get_db)):
    """[REQ-USER-002 / NFR-USER-001] Login ha JWT me'ẽ"""
    user = db.execute(select(User).where(User.email == login_data.email)).scalars().first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail térã ñe'ẽñemi oĩ vai.")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Ko kuatiañe'ẽ ndoikói.")
        
    if user.role == RoleEnum.PENDING:
        raise HTTPException(status_code=401, detail="Eha'arõ sãmbyhyhára ñemoneĩ.")

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


@auth_router.post("/token/refresh", response_model=TokenResponse)
def refresh_token_endpoint(refresh_token: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    """[NFR-USER-001] Token ñembopyahu mbohovái guasu"""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token ndoikói cookie-pe.")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token payload oĩ vai.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token opáma. Emoñepyrũ jey sesión.")

    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User ndoikói.")

    new_access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": new_access_token, "token_type": "bearer"}


@auth_router.post("/logout")
def logout_user(response: Response):
    """[REQ-USER-003] Sesión ñembogue ha cookie mbogue"""
    response.delete_cookie(key="refresh_token", httponly=True, samesite="strict")
    return {"message": "Esẽma porã."}


# ==========================================
# 🚀 User Router kuatia (/api/v1/users)
# ==========================================

@user_router.get("", response_model=List[UserResponse])
def get_user_list(
    search: Optional[str] = None,
    department: Optional[DepartmentEnum] = None,
    db: Session = Depends(get_db)
):
    """[REQ-USER-004] Sãmbyhyhára ohecha hag̃ua user-kuéra tyvy"""
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


@user_router.patch("/{user_id}/role")
def change_user_role(user_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-005] Sãmbyhyhára omoambue hag̃ua user role"""
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User ndojehupytýi.")
    
    user.role = role_data.role
    db.commit()
    return {
        "message": "User role oñemoambue porã.",
        "user_id": user.id,
        "changed_role": user.role
    }


@user_router.get("/me", response_model=UserResponse)
def get_my_profile(db: Session = Depends(get_db)):
    """[REQ-USER-006] Che profile jehecha (Mbohovái 4)"""
    dummy_user = db.execute(select(User)).scalars().first()
    if not dummy_user:
        raise HTTPException(status_code=404, detail="User ndoĩri.")
    return dummy_user


@user_router.patch("/me", response_model=UserResponse)
def update_my_profile(update_data: UserUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-007] Che profile ñemoambue voreve"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User ñemoambue hag̃ua ndoĩri.")

    if update_data.department is not None:
        user.department = update_data.department
    if update_data.phone_number is not None:
        exist_phone = db.execute(
            select(User).where(User.phone_number == update_data.phone_number, User.id != user.id)
        ).scalars().first()
        if exist_phone:
            raise HTTPException(status_code=400, detail="Ambue user oiporúma ko pumbyry.")
        user.phone_number = update_data.phone_number

    db.commit()
    db.refresh(user)
    return user


@user_router.patch("/me/password")
def change_my_password(pwd_data: PasswordUpdate, db: Session = Depends(get_db)):
    """[REQ-USER-008] Che ñe'ẽñemi ñemoambue PATCH rupive (Mbohovái 3)"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User ndojehupytýi.")

    if not verify_password(pwd_data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Ñe'ẽñemi ymaguare oĩ vai.")

    user.hashed_password = get_password_hash(pwd_data.new_password)
    db.commit()
    return {"message": "Ñe'ẽñemi oñemoambue porã."}


@user_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def withdraw_my_account(db: Session = Depends(get_db)):
    """[REQ-USER-009] Che kuatiañe'ẽ mbogue (Mbohovái 6)"""
    user = db.execute(select(User)).scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User mbogue hag̃ua ndoĩri.")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)