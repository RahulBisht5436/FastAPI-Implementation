"""
Review API routes.

All endpoints under /review are defined here and registered in main.py
via app.include_router(reviews_router).
"""

from turtle import update
from fastapi import APIRouter, Depends , Query
from sqlmodel import Session, select, func

# Review       -> database table model (maps to the `review` table)
# ReviewCreate -> validates incoming POST body (no id / created_at)
# ReviewRead   -> shapes the API response after a row is saved
# ReviewUpdate -> reserved for future PATCH/PUT endpoints
from Models.SQLModel import Review, ReviewCreate, ReviewUpdate, ReviewRead

# get_session is a FastAPI dependency that opens one DB session per request
from Data.database import get_session

# APIRouter groups related endpoints; prefix="/review" means all paths start with /review
route = APIRouter(prefix="/review", tags=["review"])


@route.get("/check_review_health")
def review_root():
    """Simple health check to confirm this router is mounted correctly."""
    return {
        "status": 200,
        "message": "review router are healthy",
    }


@route.post("/", response_model=ReviewRead)
def create_review(review: ReviewCreate, session: Session = Depends(get_session)):
    """
    Create a new review and persist it to the database.

    Args:
        review:  JSON body, validated against ReviewCreate (play_name, reviewer_name, rating, comment)
        session: Injected by FastAPI via Depends(get_session) — one session per request

    Returns:
        The saved row as ReviewRead (includes auto-generated id and created_at)
    """
    # Convert validated input (ReviewCreate) into a database row object (Review).
    # model_dump() turns the Pydantic object into a plain dict; ** unpacks it as keyword args.
    db_review = Review(**review.model_dump())

    # Stage the new row in the current transaction (not yet written to disk)
    session.add(db_review)

    # Persist the transaction — without commit(), nothing is saved to rangmanch.db
    session.commit()

    # Reload the row from the DB so id and created_at are populated on db_review
    session.refresh(db_review)

    return db_review



@route.get("/get_reviews", response_model=list[Review])
def get_reviews(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """
    Fetch a paginated list of reviews from the database.

    Query params (read from the URL, e.g. /get_reviews?page=2&limit=5):
        page:  Which page to return (starts at 1)
        limit: How many reviews per page (max 100)

    Returns:
        A list of Review objects for the requested page
    """
    # Convert page number into a SQL OFFSET.
    # Page 1 -> skip 0 rows, Page 2 -> skip `limit` rows, Page 3 -> skip 2 * limit, etc.
    offset = (page - 1) * limit

    # Build a SELECT query: fetch Review rows, skip `offset`, return at most `limit` rows
    statement = (
        select(Review)
        .offset(offset)
        .limit(limit)
    )

    # Execute the query and collect all matching rows as a Python list
    reviews = session.exec(statement).all()

    return reviews


@route.get("/average/{playname}")
def averageRating(
    playname: str,
    session: Session = Depends(get_session),
):
    """
    Return the average rating for all reviews of a given play.

    Path param:
        playname: The play name to aggregate ratings for (e.g. /average/Macbeth)

    Returns:
        The mean rating as a float, or null if no reviews exist for that play
    """
    # func.avg() runs SQL AVG() — computes the mean of the rating column
    # .where() filters rows so only reviews for this play_name are included
    query = select(func.avg(Review.rating)).where(
        Review.play_name == playname
    )

    # .one() returns a single scalar result (the average value)
    average = session.exec(query).one()

    return average

@route.get("/get_review/{reviewID}", response_model=ReviewRead)
def get_review(
    reviewID: int,
    session: Session = Depends(get_session)
):

    query = select(Review).where(Review.id == reviewID)

    review = session.exec(query).one()

    return review

from fastapi import Depends, HTTPException
from sqlmodel import Session, select


@route.patch("/update_review/{reviewID}", response_model=ReviewRead)
def update_review(
    reviewID: int,
    review: ReviewUpdate,
    session: Session = Depends(get_session)
):

    # 1. Find the existing review
    query = select(Review).where(Review.id == reviewID)

    existing_review = session.exec(query).first()

    # 2. If it doesn't exist
    if existing_review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    # 3. Get only the fields the user actually sent
    review_data = review.model_dump(exclude_unset=True)

    # 4. Update those fields
    existing_review.sqlmodel_update(review_data)

    # 5. Save changes
    session.add(existing_review)
    session.commit()

    # 6. Refresh object from database
    session.refresh(existing_review)

    return existing_review