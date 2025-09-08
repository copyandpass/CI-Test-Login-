# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

# 데이터베이스 URL (실제 환경에서는 환경 변수로 관리)
DATABASE_URL = "mysql+pymysql://root:1111@mariadb:3306/my_login_db"

# SQLAlchemy 설정
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 비밀번호 해시를 위한 CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI 앱 인스턴스
app = FastAPI()

# 데이터베이스 세션을 가져오는 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))

# 테이블 생성 (없을 경우)
Base.metadata.create_all(bind=engine)

# Pydantic 스키마 정의 (요청/응답 모델)
class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    
# 비밀번호 해시 함수
def hash_password(password: str):
    return pwd_context.hash(password)

# 비밀번호 검증 함수
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI App!"}

# 사용자 회원가입 엔드포인트
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserIn, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자 이름입니다."
        )
    
    hashed_pwd = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pwd)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터베이스 오류: {e}"
        )

    return {"message": f"'{new_user.username}' 님, 회원가입을 환영합니다!"}

# 사용자 로그인 엔드포인트
@app.post("/login", response_model=UserOut)
def login(user: UserIn, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자 이름 또는 비밀번호입니다."
        )
    return db_user
// 메인 코드 끝