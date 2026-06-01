from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

# 기본 제공 데이터
user_list = [
    {
        "id": 1,
        "name": "홍길동",
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!"
    },
    {
        "id": 2,
        "name": "장문복",
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!"
    },
    {
        "id": 3,
        "name": "임우진",
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@"
    }
]

# Request Body를 위한 Pydantic 모델 정의
class UserCreate(BaseModel):
    id: int
    name: str
    age: int
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    age: int
    email: EmailStr

# 1. 모든 회원의 정보를 목록으로 조회하는 API
@router.get("/users")
def get_all_users():
    return user_list

# 2. 특정 회원의 정보를 조회하는 API (ID 기준)
@router.get("/users/{user_id}")
def get_user(user_id: int):
    for user in user_list:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# 3. 회원의 정보를 입력받아 추가하는 API
@router.post("/users")
def create_user(user: UserCreate):
    # 중복 ID 체크 (선택)
    for existing_user in user_list:
        if existing_user["id"] == user.id:
            raise HTTPException(status_code=400, detail="ID already exists")
    
    new_user = user.model_dump() # Pydantic 모델을 딕셔너리로 변환
    user_list.append(new_user)
    return {"message": "User created successfully", "user": new_user}

# 4. 특정 회원의 나이와 이메일을 수정하는 API
@router.put("/users/{user_id}")
def update_user(user_id: int, update_data: UserUpdate):
    for user in user_list:
        if user["id"] == user_id:
            user["age"] = update_data.age
            user["email"] = update_data.email
            return {"message": "User updated successfully", "user": user}
    raise HTTPException(status_code=404, detail="User not found")

# 5. 특정 회원의 정보를 삭제하는 API
@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    for idx, user in enumerate(user_list):
        if user["id"] == user_id:
            deleted_user = user_list.pop(idx)
            return {"message": "User deleted successfully", "user": deleted_user}
    raise HTTPException(status_code=404, detail="User not found")