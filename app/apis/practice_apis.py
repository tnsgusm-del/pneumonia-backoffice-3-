from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
import re

router = APIRouter(prefix="/practice_api", tags=["Practice"])

user_list = [
    {"id": 1, "name": "홍길동", "age": 24, "email": "gildong24@example.com", "password": "Password1234!!"},
    {"id": 2, "name": "장문복", "age": 21, "email": "moonluck12@example.com", "password": "Check1321!"},
    {"id": 3, "name": "임우진", "age": 31, "email": "limousine33@example.com", "password": "lwsPAssword12@"}
]

class UserResponse(BaseModel):
    id: int
    name: str
    age: int
    email: str

class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    password: str

    @field_validator("name")
    def validate_name(cls, v):
        if len(v) < 2 or len(v) > 10:
            raise ValueError("이름은 2자 이상 10자 이하여야 합니다.")
        return v

    @field_validator("age")
    def validate_age(cls, v):
        if v < 14:
            raise ValueError("나이는 14세 이상이어야 합니다.")
        return v

    @field_validator("email")
    def validate_email(cls, v):
        if len(v) > 30:
            raise ValueError("이메일은 30자 이하여야 합니다.")
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        if any(u["email"] == v for u in user_list):
            raise ValueError("이미 사용 중인 이메일입니다.")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 20:
            raise ValueError("비밀번호는 8자 이상 20자 이하여야 합니다.")
        if not re.search(r'[A-Z]', v):
            raise ValueError("비밀번호에 대문자가 1개 이상 필요합니다.")
        if not re.search(r'[a-z]', v):
            raise ValueError("비밀번호에 소문자가 1개 이상 필요합니다.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("비밀번호에 특수문자가 1개 이상 필요합니다.")
        return v

class UserUpdate(BaseModel):
    age: Optional[int] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("age")
    def validate_age(cls, v):
        if v is not None and v < 14:
            raise ValueError("나이는 14세 이상이어야 합니다.")
        return v

    @field_validator("email")
    def validate_email(cls, v):
        if v is not None:
            if len(v) > 30:
                raise ValueError("이메일은 30자 이하여야 합니다.")
            pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(pattern, v):
                raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8 or len(v) > 20:
                raise ValueError("비밀번호는 8자 이상 20자 이하여야 합니다.")
            if not re.search(r'[A-Z]', v):
                raise ValueError("비밀번호에 대문자가 1개 이상 필요합니다.")
            if not re.search(r'[a-z]', v):
                raise ValueError("비밀번호에 소문자가 1개 이상 필요합니다.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
                raise ValueError("비밀번호에 특수문자가 1개 이상 필요합니다.")
        return v

@router.get("/users", response_model=list[UserResponse])
def get_users():
    return user_list

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    new_id = max(u["id"] for u in user_list) + 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "age": user.age,
        "email": user.email,
        "password": user.password
    }
    user_list.append(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate):
    if user.age is None and user.email is None and user.password is None:
        raise HTTPException(status_code=400, detail="수정할 항목을 1개 이상 입력해주세요.")
    for u in user_list:
        if u["id"] == user_id:
            if user.age is not None:
                u["age"] = user.age
            if user.email is not None:
                u["email"] = user.email
            if user.password is not None:
                u["password"] = user.password
            return u
    raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")

@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, u in enumerate(user_list):
        if u["id"] == user_id:
            user_list.pop(i)
            return {"message": f"회원 {user_id}번이 삭제되었습니다."}
    raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다.")
