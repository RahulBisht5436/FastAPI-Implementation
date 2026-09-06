from pathlib import Path

from sqlmodel import Session, create_engine, SQLModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = BASE_DIR / "DataBase"
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = DATABASE_DIR / "orders.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Get a session for the database"""
    with Session(engine) as session:
        yield session
