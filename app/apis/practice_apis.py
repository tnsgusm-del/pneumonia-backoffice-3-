<<<<<<< HEAD
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
=======
import re
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/practice_api", tags=["Practice User API"])

user_list = [
	{"id": 1, "name": "홍길동", "age": 24, "email": "gildong24@example.com", "password": "Password1234!!"},
	{"id": 2, "name": "장문복", "age": 21, "email": "moonluck12@example.com", "password": "Check1321!"},
	{"id": 3, "name": "임우진", "age": 31, "email": "limousine33@example.com", "password": "lwsPAssword12@"}
]

def validate_email_format(email: str):
    if len(email) > 30:
        raise HTTPException(status_code=400, detail="이메일은 최대 30자까지 가능합니다.")
    regex = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex, email):
        raise HTTPException(status_code=400, detail="올바른 이메일 형식이 아닙니다.")

def validate_password_format(password: str):
    if not (8 <= len(password) <= 20):
        raise HTTPException(status_code=400, detail="비밀번호는 8자 이상 20자 이하로 입력해주세요.")
    if not re.search(r"[a-z]", password) or not re.search(r"[A-Z]", password) or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(status_code=400, detail="비밀번호에는 대소문자와 특수문자가 각각 1개 이상 포함되어야 합니다.")

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=10)
    age: int = Field(..., ge=14)
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    age: int | None = Field(None, ge=14)
    email: str | None = None
    password: str | None = None

# 1. 모든 회원 정보 목록 조회
@router.get("/users")
def get_all_users():
    return [{"id": u["id"], "name": u["name"], "age": u["age"], "email": u["email"]} for u in user_list]

# 2. 특정 회원 정보 조회
@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return {"id": user["id"], "name": user["name"], "age": user["age"], "email": user["email"]}
    raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")

# 3. 회원 정보 추가
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreateRequest):
    validate_email_format(user_data.email)
    validate_password_format(user_data.password)
    
    if any(u["email"] == user_data.email for u in user_list):
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
        
    next_id = max(u["id"] for u in user_list) + 1 if user_list else 1
    new_user = {
        "id": next_id, "name": user_data.name, "age": user_data.age, "email": user_data.email, "password": user_data.password
    }
    user_list.append(new_user)
    return {"message": "회원이 성공적으로 등록되었습니다.", "user_id": next_id}

# 4. 회원 정보 수정
@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdateRequest):
    if update_data.age is None and update_data.email is None and update_data.password is None:
        raise HTTPException(status_code=400, detail="수정할 항목을 최소 하나 이상 입력해주세요.")
        
    target_user = None
    for user in user_list:
        if user["id"] == user_id:
            target_user = user
            break
            
    if not target_user:
        raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")
        
    if update_data.age is not None:
        target_user["age"] = update_data.age
    if update_data.email is not None:
        validate_email_format(update_data.email)
        target_user["email"] = update_data.email
    if update_data.password is not None:
        validate_password_format(update_data.password)
        target_user["password"] = update_data.password
        
    return {"message": "회원 정보가 수정되었습니다."}

# 5. 특정 회원 정보 삭제
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for i, user in enumerate(user_list):
        if user["id"] == user_id:
            del user_list[i]
            return {"message": "회원 정보가 삭제되었습니다."}
    raise HTTPException(status_code=404, detail="해당 ID의 회원을 찾을 수 없습니다.")
>>>>>>> 2f7f8bf105d84cad53d2470d3062a916aa471216
