# FastAPI ORM — Application Flow

This document describes how the ORM project is structured and how data flows from startup through the database layer.

---

## High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser["Browser / API Client"]
        Swagger["/docs — Swagger UI"]
    end

    subgraph App["FastAPI Application"]
        Main["main.py<br/>FastAPI app + lifespan"]
        Routes["API Routes<br/>(to be added)"]
        GetDB["get_db()<br/>Session dependency"]
    end

    subgraph ORM["SQLAlchemy ORM Layer"]
        Models["Models/databaseModel.py<br/>User model"]
        Base["Base<br/>declarative_base()"]
        SessionPool["sessionPool<br/>sessionmaker"]
        Engine["engine<br/>create_engine()"]
    end

    subgraph Config["Configuration"]
        Env[".env<br/>DB credentials"]
        Dotenv["python-dotenv<br/>load_dotenv()"]
    end

    subgraph Infra["Infrastructure"]
        Docker["docker-compose.yml<br/>PostgreSQL 16"]
        Postgres[("PostgreSQL<br/>mydatabase")]
    end

    Browser --> Main
    Swagger --> Main
    Main --> Routes
    Routes --> GetDB
    GetDB --> SessionPool
    Routes --> Models
    Models --> Base
    Main -->|"lifespan: create_all()"| Engine
    Models --> Engine
    SessionPool --> Engine
    Engine --> Postgres
    Dotenv --> Env
    Env --> Engine
    Docker --> Postgres
```

---

## Project Structure

```
ORM/
├── .env                          # Database credentials (not committed)
├── docker-compose.yml            # PostgreSQL container
├── pyproject.toml                # Dependencies & project config
├── Models/
│   └── databaseModel.py          # SQLAlchemy models (User)
└── src/orm/
    ├── main.py                   # FastAPI app entry point
    ├── databaseConnection.py     # Engine, session, Base, get_db
    └── __init__.py
```

---

## Startup Flow

When the application starts, components initialize in this order:

```mermaid
sequenceDiagram
    participant Uvicorn as Uvicorn Server
    participant Main as main.py
    participant DBConn as databaseConnection.py
    participant Dotenv as .env
    participant Engine as SQLAlchemy Engine
    participant PG as PostgreSQL

    Uvicorn->>Main: Import & create FastAPI app
    Main->>DBConn: Import engine, Base
    DBConn->>Dotenv: load_dotenv()
    Dotenv-->>DBConn: username, password, host, port
    DBConn->>Engine: create_engine(postgresql URL)
    DBConn->>Engine: sessionmaker(bind=engine)
    Note over Main: lifespan() runs on startup
    Main->>Engine: Base.metadata.create_all(engine)
    Engine->>PG: CREATE TABLE users (if not exists)
    PG-->>Engine: OK
    Engine-->>Main: Tables ready
    Main-->>Uvicorn: App ready to serve requests
```

### Startup steps (detail)

| Step | File | What happens |
|------|------|--------------|
| 1 | `databaseConnection.py` | `load_dotenv()` reads `.env` for DB credentials |
| 2 | `databaseConnection.py` | Builds PostgreSQL URL and creates `engine` |
| 3 | `databaseConnection.py` | Creates `sessionPool` (session factory) and `Base` |
| 4 | `main.py` | `lifespan` calls `Base.metadata.create_all(engine)` |
| 5 | PostgreSQL | `users` table is created from the `User` model |

> **Note:** `lifespan` is defined in `main.py` but is not yet passed to `FastAPI(lifespan=lifespan)`. Add it to enable automatic table creation on startup.

---

## Database Connection Flow

```mermaid
flowchart LR
    subgraph EnvVars["Environment (.env)"]
        U["username=postgres"]
        P["password=postgres"]
        H["host=localhost"]
        PO["port=5432"]
        D["database=mydatabase"]
    end

    subgraph DBConn["databaseConnection.py"]
        Load["load_dotenv()"]
        URL["URL.create(postgresql, ...)"]
        Eng["engine = create_engine(url)"]
        Pool["sessionPool = sessionmaker(bind=engine)"]
        BaseDef["Base = declarative_base()"]
    end

    U & P & H & PO & D --> Load
    Load --> URL
    URL --> Eng
    Eng --> Pool
    Eng --> BaseDef
```

**Connection string built:**

```
postgresql://postgres:postgres@localhost:5432/mydatabase
```

---

## Request Flow (per API call)

When you add routes that use `get_db`, each request follows this pattern:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Route as Route Handler
    participant GetDB as get_db()
    participant Session as DB Session
    participant Model as User Model
    participant PG as PostgreSQL

    Client->>FastAPI: HTTP Request (e.g. POST /users)
    FastAPI->>Route: Call endpoint
    Route->>GetDB: Depends(get_db)
    GetDB->>Session: sessionPool()
    GetDB-->>Route: yield db session
    Route->>Model: db.add(user) / db.query(User)
    Model->>Session: SQLAlchemy ORM operations
    Session->>PG: SQL (INSERT / SELECT / ...)
    PG-->>Session: Result
    Session-->>Route: Python objects
    Route-->>FastAPI: Response
    FastAPI-->>Client: JSON response
    Note over GetDB,Session: finally: db.close()
```

### `get_db` dependency (session lifecycle)

```python
def get_db():
    db = sessionPool()      # 1. Open session from pool
    try:
        yield db            # 2. Hand session to route handler
    finally:
        db.close()          # 3. Always close when request ends
```

Use in a route like:

```python
@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

---

## ORM Model Flow

```mermaid
erDiagram
    users {
        int id PK
        string name
        string email
        string password
        datetime created_at
        datetime updated_at
        datetime deleted_at
        boolean is_active
        boolean is_deleted
        boolean is_verified
        boolean is_admin
    }
```

### How a model maps to the database

```mermaid
flowchart TD
    A["User class inherits Base"] --> B["__tablename__ = 'users'"]
    B --> C["Column definitions<br/>(id, name, email, ...)"]
    C --> D["Base.metadata.create_all(engine)"]
    D --> E["PostgreSQL: users table"]
```

| Python (`User`) | PostgreSQL (`users`) |
|-----------------|----------------------|
| `id` (Integer, PK) | `id` SERIAL PRIMARY KEY |
| `name` (String) | `name` VARCHAR |
| `email` (String) | `email` VARCHAR |
| `password` (String) | `password` VARCHAR |
| `created_at` (DateTime) | `created_at` TIMESTAMP |
| `is_active` (Boolean) | `is_active` BOOLEAN |
| ... | ... |

---

## Docker + Local Dev Flow

```mermaid
flowchart TB
    subgraph DevMachine["Your Machine"]
        EnvFile[".env<br/>host=localhost:5432"]
        FastAPIApp["FastAPI App<br/>uvicorn src.orm.main:app"]
    end

    subgraph Docker["Docker Compose"]
        Compose["docker-compose up -d"]
        Container["sqlalchemy_postgres<br/>postgres:16"]
        Volume["postgres_data volume"]
    end

    Compose --> Container
    Container --> Volume
    FastAPIApp -->|"psycopg2 / SQLAlchemy"| Container
    EnvFile -.->|"credentials match"| Container
```

### Run order

1. **Start database:** `docker-compose up -d`
2. **Verify `.env`** matches `docker-compose.yml` (user, password, db name)
3. **Start API:** `uvicorn src.orm.main:app --reload`
4. **Open docs:** http://localhost:8000/docs

---

## Component Dependency Graph

```mermaid
flowchart BT
    Env[".env"]
    Docker["docker-compose.yml"]

    DBConn["databaseConnection.py"]
    Model["databaseModel.py"]
    Main["main.py"]

    Env --> DBConn
    Docker -->|"provides PostgreSQL"| DBConn
    DBConn -->|"Base, engine"| Model
    DBConn -->|"engine, Base, get_db"| Main
    Model -->|"User"| Main
```

---

## Data Flow Summary

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────────┐
│   .env      │────▶│ database     │────▶│  SQLAlchemy     │────▶│ PostgreSQL │
│  (config)   │     │ Connection   │     │  Engine/Session │     │ (Docker)   │
└─────────────┘     └──────────────┘     └─────────────────┘     └────────────┘
                            │                      ▲
                            ▼                      │
                     ┌──────────────┐     ┌─────────────────┐
                     │ database     │────▶│  Base.metadata  │
                     │ Model (User) │     │  create_all()   │
                     └──────────────┘     └─────────────────┘
                            ▲
                            │
                     ┌──────────────┐
                     │   main.py    │
                     │  FastAPI app │
                     └──────────────┘
                            ▲
                            │
                     ┌──────────────┐
                     │ HTTP Client  │
                     └──────────────┘
```

---

## Key Files Reference

| File | Role |
|------|------|
| `docker-compose.yml` | Runs PostgreSQL 16 on port 5432 |
| `.env` | Stores `username`, `password`, `host`, `port`, `database` |
| `src/orm/databaseConnection.py` | Engine, session pool, `Base`, `get_db()` |
| `Models/databaseModel.py` | `User` table definition |
| `src/orm/main.py` | FastAPI app, lifespan (table creation) |

---

## Next Steps (typical extension)

```mermaid
flowchart LR
    A["Add routes in main.py"] --> B["Use Depends(get_db)"]
    B --> C["CRUD on User model"]
    C --> D["Pydantic schemas for request/response"]
    D --> E["Wire lifespan to FastAPI()"]
```

1. Pass `lifespan=lifespan` to `FastAPI(...)` so tables are created on startup.
2. Add Pydantic schemas for request/response validation.
3. Add CRUD endpoints (`GET /users`, `POST /users`, etc.) using `Depends(get_db)`.
