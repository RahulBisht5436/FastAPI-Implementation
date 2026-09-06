# here SQL Model defines how the table and valiation model are defined
# session tell to communicate with the SQL DB
# engine is the program which actually know how to interact with the DB
from pathlib import Path

from sqlmodel import SQLModel , Session , create_engine

from Models.SQLModel import Review  # noqa: F401 - registers table with metadata

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'rangmanch.db'}"

# create engine creates engine with this database information
engine  = create_engine(DATABASE_URL , echo=True)
# this echo show the sql Queries inside the cmd that are generate by the SQL model

# need to understand what is happening inside this 
def create_tables():
    """ Create all tables defined by SQLModel class """
    SQLModel.metadata.create_all(engine)
    # internally SQL Model and SQLAlcemy store data regrading the table inside the metadata 
    
    
    
#also need to understand this
def get_session():
    """ dependency that provides a database session per request """
    
    # using the with Session(engine) starts the session
    # it conceptually equivalent to the open file 
    with Session(engine) as session:
        yield session