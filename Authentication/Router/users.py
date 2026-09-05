# User API routes — HTTP endpoints for creating and listing users.
# Registered in main.py via app.include_router(user_router).
#
# Endpoints:
#   POST /users/  → create a new user
#   GET  /users/  → list users with pagination

from fastapi import APIRouter , HTTPException, Depends , Query  # Query = query-string params (?page=1&limit=10)
from sqlmodel import Session ,select                              # Session = DB connection; select = SQL SELECT builder
from Database.database import get_session                        # Dependency that yields a DB session per request
from Models.user import Users                                    # Table model for users
from Models.books import Book                                    # Imported so relationships resolve if needed

from dotenv import load_dotenv
from os import getenv

load_dotenv()                          # Load variables from .env file into the environment
API_KEY = getenv("API_KEY")            # Secret key used to authorize API requests

from src.authentication.authenticatio import verify_token  # Checks x-token header before route runs

# APIRouter groups related endpoints under a common URL prefix and OpenAPI tag.
router = APIRouter(
    prefix="/users",   # All routes here start with /users (e.g. POST /users/, GET /users/)
    tags=["users"]     # Groups these endpoints under "users" in Swagger docs at /docs
)


# ---------------------------------------------------------------------------
# POST /users/ — Create a new user
# ---------------------------------------------------------------------------
@router.post("/", response_model=Users)
async def create_user(
    user: Users,                                      # Request body — validated against Users schema
    session: Session = Depends(get_session),          # Injected DB session (opened before, closed after request)
    api_key: str = Depends(verify_token),             # Injected token from x-token header (401 if invalid)
):
    # Extra check against env API_KEY (verify_token already validates the header once).
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check if a user with this email already exists in the database.
    existing_user = session.exec(select(Users).where(Users.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Build a new Users row (id is auto-assigned by the DB on commit).
    user = Users(name=user.name, email=user.email, college=user.college)
    session.add(user)       # Stage the new row for insert
    session.commit()        # Write to database
    session.refresh(user)   # Reload row so id and other DB defaults are populated
    return user.model_dump()  # Return as plain dict (single object — .model_dump() works here)


# ---------------------------------------------------------------------------
# GET /users/ — List users with pagination
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[Users])
async def get_users(
    page: int = Query(default=1, ge=1),               # Page number (1-based); must be >= 1
    limit: int = Query(default=10, ge=1),             # Rows per page; must be >= 1
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_token),
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Convert page number to SQL OFFSET (page 1 → skip 0, page 2 → skip limit, etc.).
    offset = (page - 1) * limit
    statement = select(Users).offset(offset).limit(limit)
    users = session.exec(statement).all()  # Returns a list of Users objects

    # .all() returns a list — call .model_dump() on each user, not on the list itself.
    return [user.model_dump() for user in users]
