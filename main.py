

# main.py
from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine, Base
from models import User
from schemas import UserCreate
from starlette.responses import JSONResponse, RedirectResponse


# Create DB tables (will create if not exist)
Base.metadata.create_all(bind=engine)

# Initialize AUTO_INCREMENT to start at 1000
def init_user_id_sequence():
    """Ensure user IDs start from 1000"""
    try:
        with engine.begin() as conn:
            # Check if table exists and get current max ID
            result = conn.execute(text("SELECT MAX(id) as max_id FROM users"))
            max_id_row = result.fetchone()
            max_id = max_id_row[0] if max_id_row and max_id_row[0] is not None else 0
            
            # Always ensure AUTO_INCREMENT is at least 1000
            if max_id < 1000:
                next_id = 1000
            else:
                next_id = max_id + 1
            
            # Force set AUTO_INCREMENT to the next ID
            conn.execute(text(f"ALTER TABLE users AUTO_INCREMENT = {next_id}"))
            print(f"✅ AUTO_INCREMENT set to {next_id} (max_id was: {max_id})")
    except Exception as e:
        print(f"⚠️ Warning: Could not set AUTO_INCREMENT: {e}")
        # Try to set it anyway after a short delay
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE users AUTO_INCREMENT = 1000"))
                print("✅ AUTO_INCREMENT set to 1000 (fallback)")
        except Exception as e2:
            print(f"⚠️ Could not set AUTO_INCREMENT (fallback): {e2}")

# Set AUTO_INCREMENT immediately after table creation
init_user_id_sequence()

app = FastAPI(title="WeatherInfo Auth (simple)")

# Initialize user ID sequence on startup using FastAPI startup event (double-check)
@app.on_event("startup")
def startup_event():
    """Initialize AUTO_INCREMENT on server startup"""
    print("🔄 Running startup event to verify AUTO_INCREMENT...")
    init_user_id_sequence()


# Allow browser requests from your front-end (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def signup(
    name: str = Form(...),
    phone: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Accepts form-data (from an HTML form) and inserts a user record into MySQL.
    No authentication; simple insert.
    """

    # Basic duplicate email check
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure AUTO_INCREMENT is at least 1000 before creating user
    try:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT MAX(id) as max_id FROM users"))
            max_id_row = result.fetchone()
            max_id = max_id_row[0] if max_id_row and max_id_row[0] is not None else 0
            
            # If table is empty or max_id < 1000, set AUTO_INCREMENT to 1000
            if max_id < 1000:
                conn.execute(text("ALTER TABLE users AUTO_INCREMENT = 1000"))
                print(f"✅ Setting AUTO_INCREMENT to 1000 (current max: {max_id})")
    except Exception as e:
        print(f"⚠️ Warning: Could not check/set AUTO_INCREMENT: {e}")

    user = User(
        name=name,
        phone=phone,
        email=email,
        password=password  # Storing plain text password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Verify the user got an ID >= 1000
    if user.id < 1000:
        print(f"⚠️ Warning: User got ID {user.id} which is less than 1000. This should not happen.")

    # Return a simple JSON response (or redirect)
    return JSONResponse(status_code=201, content={"message": "User created", "user_id": user.id})


@app.post("/signin")
def signin(
    identifier: str = Form(...),  # email or phone
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Sign in endpoint that accepts email/phone and password.
    """
    
    # Try to find user by email first, then by phone
    user = db.query(User).filter(User.email == identifier).first()
    if not user:
        user = db.query(User).filter(User.phone == identifier).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Direct password comparison (plain text)
    if password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Return success response
    return JSONResponse(status_code=200, content={
        "message": "Sign in successful", 
        "user_id": user.id,
        "name": user.name,
        "email": user.email
    })
