# Book API routes — HTTP endpoints for creating and reading books.
# Registered in main.py via app.include_router(book_router).
#
# Endpoints:
#   POST   /books/          → create a new book
#   GET    /books/          → list books with pagination
#   GET    /books/{book_id} → get a single book by id

from fastapi import APIRouter , HTTPException, Depends , Query  # Query = query-string params (?page=1&limit=10)
from sqlmodel import Session ,select                              # Session = DB connection; select = SQL SELECT builder
from Database.database import get_session                        # Dependency that yields a DB session per request
from Models.books import Book , BookCreate , BookRead            # Book = table model; BookCreate/BookRead = request/response schemas
from src.authentication.authenticatio import verify_token        # Checks x-token header before route runs
from dotenv import load_dotenv
from os import getenv

load_dotenv()                          # Load variables from .env file into the environment
API_KEY = getenv("API_KEY")            # Secret key used to authorize API requests

# APIRouter groups related endpoints under a common URL prefix and OpenAPI tag.
router = APIRouter(
    prefix="/books",   # All routes here start with /books (e.g. POST /books/, GET /books/1)
    tags=["books"]     # Groups these endpoints under "books" in Swagger docs at /docs
)


# ---------------------------------------------------------------------------
# POST /books/ — Create a new book
# ---------------------------------------------------------------------------
# Request body uses BookCreate (no id — assigned by DB).
# Response uses BookRead (includes id after save).
@router.post("/", response_model=BookRead)
async def create_book(
    book: BookCreate,                                 # Request body — validated against BookCreate schema
    session: Session = Depends(get_session),          # Injected DB session (opened before, closed after request)
    api_key: str = Depends(verify_token),             # Injected token from x-token header (401 if invalid)
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Convert request schema (BookCreate) → table model (Book) before saving.
    # Use db_book — do NOT session.add(book), because book is BookCreate, not a DB row.
    db_book = Book(
        title=book.title,
        author=book.author,
        description=book.description,
        price=book.price,
        is_sold=book.is_sold,
        user_id=book.user_id,   # Must reference an existing user id in the users table
    )

    session.add(db_book)       # Stage the new row for insert
    session.commit()           # Write to database
    session.refresh(db_book)   # Reload row so id and other DB defaults are populated
    return db_book.model_dump()


# ---------------------------------------------------------------------------
# GET /books/ — List books with pagination
# ---------------------------------------------------------------------------
@router.get("/", response_model=list[BookRead])
async def get_books(
    page: int = Query(default=1, ge=1),               # Page number (1-based); must be >= 1
    limit: int = Query(default=10, ge=1),             # Rows per page; must be >= 1
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_token),
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Convert page number to SQL OFFSET (page 1 → skip 0, page 2 → skip limit, etc.).
    offset = (page - 1) * limit
    statement = select(Book).offset(offset).limit(limit)
    books = session.exec(statement).all()  # Returns a list of Book objects

    # Returning ORM objects directly works — FastAPI serializes via response_model=list[BookRead].
    return books


# ---------------------------------------------------------------------------
# GET /books/{book_id} — Get a single book by primary key
# ---------------------------------------------------------------------------
@router.get("/{book_id}", response_model=BookRead)
async def get_book(
    book_id: int,                                     # Path parameter from URL (e.g. /books/3 → book_id=3)
    session: Session = Depends(get_session),
    api_key: str = Depends(verify_token),
):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    statement = select(Book).where(Book.id == book_id)
    book = session.exec(statement).first()  # Returns one Book or None if not found

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book.model_dump()

# Example POST /books/ request body:
# {
#     "title": "The Great Gatsby",
#     "author": "F. Scott Fitzgerald",
#     "description": "A story of love and loss in the Jazz Age",
#     "price": 12.99,
#     "is_sold": false,
#     "user_id": 1
# }
