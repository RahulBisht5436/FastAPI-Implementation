"""
Login route — authenticates a user and returns a JWT access token.

POST /login/
  Body: { "email": "...", "password": "..." }
  Response: { "message": "Login successful", "access_token": "<jwt>" }
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from src.orm.databaseConnection import get_db
from Models.databaseModel import User
from Utilities.encrypt import verify_password
from Utilities.JWTTokken import create_access_token

router = APIRouter(prefix="/login", tags=["login"])


@router.post("/")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = db.query(User).filter(User.email == email).first()

    # Generic error message — don't reveal whether email or password was wrong
    if not user:
        raise HTTPException(status_code=404, detail="User or Password is incorrect")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="User or Password is incorrect")

    access_token = create_access_token(user)

    return {"message": "Login successful", "access_token": access_token}
