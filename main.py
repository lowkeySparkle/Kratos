from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import Base, engine, User, get_db


password_hash = PasswordHash.recommended()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


class EchoRequest(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


@app.post("/echo")
def echo(data: EchoRequest):
    return {
        "message": "Data received successfully",
        "data": data.model_dump(),
    }


@app.post("/signup", status_code=201)
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == str(data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    hashed_password = password_hash.hash(data.password)

    user = User(
        email=str(data.email),
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully",
        "id": user.id,
        "email": user.email,
    }