"""
User CRUD routes.

Endpoints:
  GET    /user/all              → list all non-deleted users
  POST   /user/create           → register a new user (password is hashed before saving)
  GET    /user/{user_id}        → get a single user by id
  PUT    /user/edit/{user_id}   → update own profile (requires JWT)
  DELETE /user/delete/{user_id} → soft-delete own account (requires JWT)

Protected routes expect header:  token: Bearer <jwt>
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.orm.databaseConnection import get_db
from Models.databaseModel import User, UserCreate, UserUpdate
from Utilities.encrypt import hash_password
from Utilities.JWTTokken import verify_access_token

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/all")
def get_users(db: Session = Depends(get_db)):
    """Return all users that have not been soft-deleted."""
    users = db.query(User).filter(User.is_deleted == False).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@router.post("/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user. Password is bcrypt-hashed before being stored."""
    hashed_password = hash_password(user.password)

    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        phone=user.phone,
        address=user.address,
        city=user.city,
        state=user.state,
        zip=user.zip,
        country=user.country,
        is_admin=user.is_admin,
        is_active=user.is_active,
        is_deleted=user.is_deleted,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        deleted_at=user.deleted_at,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # reload from DB to get auto-generated fields (id, etc.)
    return db_user


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user by primary key."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_deleted:
        raise HTTPException(status_code=404, detail="User is deleted")
    if user.is_active:
        raise HTTPException(status_code=404, detail="User is not active")
    if user.is_verified:
        raise HTTPException(status_code=404, detail="User is not verified")
    if user.is_admin:
        raise HTTPException(status_code=404, detail="User is not admin")
    if user.is_active:
        raise HTTPException(status_code=404, detail="User is not active")
    if user.is_verified:
        raise HTTPException(status_code=404, detail="User is not verified")
    return user


@router.put("/edit/{user_id}")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_access_token),
):
    """
    Update the authenticated user's profile.

    Only the user themselves can edit their record (matched via JWT `sub` claim).
    Send only the fields you want to change in the request body.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # JWT `sub` is a string; user.id is an int — cast before comparing
    if int(current_user["sub"]) != db_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if user_data.email:
        db_user.email = user_data.email
    # ... update other fields as needed

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_access_token),
):
    """
    Soft-delete the authenticated user's account (sets is_deleted = True).

    The row stays in the database but is excluded from /user/all queries.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if int(current_user["sub"]) != db_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    db_user.is_deleted = True
    db.commit()
    db.refresh(db_user)
    return db_user
