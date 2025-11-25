from fastapi import FastAPI, HTTPException, Query, Depends
from models import (
    User, UserCreate, UserWithToken,
    Category, CategoryCreate,
    Record, RecordCreate,
    Account, AccountDeposit,
)
from sqlalchemy.orm import Session
from database import get_db, init_db
from db_models import UserORM, CategoryORM, RecordORM, AccountORM
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from datetime import datetime
from fastapi.openapi.docs import get_swagger_ui_html
from config import (
    API_TITLE,
    API_VERSION,
    OPENAPI_URL_PREFIX,
    OPENAPI_SWAGGER_UI_PATH,
    OPENAPI_SWAGGER_UI_URL,
    REDOC_PATH,
)
from contextlib import asynccontextmanager
from auth import get_password_hash, verify_password, create_access_token, jwt_required
from auth import JWTExpiredError, JWTInvalidError, JWTMissingError
from fastapi.responses import JSONResponse as FastJSONResponse
from fastapi import status as _status

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    openapi_url=f"{OPENAPI_URL_PREFIX}openapi.json",
    docs_url=None,  
    redoc_url=REDOC_PATH,
)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    openapi_url=f"{OPENAPI_URL_PREFIX}openapi.json",
    docs_url=None,  # disable default docs to serve custom swagger using CDN
    redoc_url=REDOC_PATH,
    lifespan=app_lifespan,
)


@app.get(OPENAPI_SWAGGER_UI_PATH, include_in_schema=False)
def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{API_TITLE} - Swagger UI",
        swagger_js_url=f"{OPENAPI_SWAGGER_UI_URL}/swagger-ui-bundle.js",
        swagger_css_url=f"{OPENAPI_SWAGGER_UI_URL}/swagger-ui.css",
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": exc.status_code, "error": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": 500, "error": str(exc)}
    )

@app.post("/register", response_model=UserWithToken, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(UserORM).filter(UserORM.name == user.name).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = get_password_hash(user.password)
    obj = UserORM(name=user.name, password=hashed)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    acc = AccountORM(user_id=obj.id, balance=0)
    db.add(acc)
    db.commit()
    db.refresh(obj)
    
    access_token = create_access_token({"sub": str(obj.id)})
    return {
        "id": obj.id,
        "name": obj.name,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/login", response_model=UserWithToken)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    # Authenticate by name and password
    user = db.query(UserORM).filter(UserORM.name == user_data.name).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token({"sub": str(user.id)})
    return {
        "id": user.id,
        "name": user.name,
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not obj:
        raise HTTPException(404, "User not found")
    return obj

@app.get("/users", response_model=list[User])
def list_users(db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    return db.query(UserORM).all()

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot delete other users")
    obj = db.query(UserORM).filter(UserORM.id == user_id).first()
    if not obj:
        raise HTTPException(404, "User not found")
    db.delete(obj)
    db.commit()
    return JSONResponse(status_code=204, content=None)

@app.post("/categories/", response_model=Category, status_code=201)
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = CategoryORM(title=category.title)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/categories/{category_id}", response_model=Category)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = db.query(CategoryORM).filter(CategoryORM.id == category_id).first()
    if not obj:
        raise HTTPException(404, "Category not found")
    return obj

@app.get("/categories", response_model=list[Category])
def list_categories(db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    return db.query(CategoryORM).all()

@app.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = db.query(CategoryORM).filter(CategoryORM.id == category_id).first()
    if not obj:
        raise HTTPException(404, "Category not found")
    db.delete(obj)
    db.commit()
    return JSONResponse(status_code=204, content=None)

@app.post("/records/", response_model=Record, status_code=201)
def create_record(record: RecordCreate, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    # Only allow creating records for the authenticated user
    if current_user.id != record.user_id:
        raise HTTPException(status_code=403, detail="Cannot create records for other users")
    if not db.query(UserORM).filter(UserORM.id == record.user_id).first():
        raise HTTPException(404, "User not found")
    if not db.query(CategoryORM).filter(CategoryORM.id == record.category_id).first():
        raise HTTPException(404, "Category not found")
    acc = db.query(AccountORM).filter(AccountORM.user_id == record.user_id).first()
    if not acc:
        raise HTTPException(404, "Account not found")
    if acc.balance is None:
        acc.balance = 0
    if acc.balance < record.amount:
        raise HTTPException(400, "Insufficient funds")

    from decimal import Decimal
    acc.balance = acc.balance - Decimal(record.amount)
    obj = RecordORM(
        user_id=record.user_id,
        category_id=record.category_id,
        amount=record.amount,
        timestamp=record.timestamp,
    )
    db.add(obj)
    db.add(acc)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/records/{record_id}", response_model=Record)
def get_record(record_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = db.query(RecordORM).filter(RecordORM.id == record_id).first()
    if not obj:
        raise HTTPException(404, "Record not found")
    return obj

@app.get("/records", response_model=list[Record])
def list_records(user_id: int | None = Query(None, ge=1), category_id: int | None = Query(None, ge=1), db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    query = db.query(RecordORM)
    if user_id is not None:
        query = query.filter(RecordORM.user_id == user_id)
    if category_id is not None:
        query = query.filter(RecordORM.category_id == category_id)
    return query.all()

@app.delete("/records/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    obj = db.query(RecordORM).filter(RecordORM.id == record_id).first()
    if not obj:
        raise HTTPException(404, "Record not found")
    # only owner can delete their record
    if obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete other user's record")
    db.delete(obj)
    db.commit()
    return JSONResponse(status_code=204, content=None)

@app.get("/accounts/{user_id}", response_model=Account)
def get_account(user_id: int, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    acc = db.query(AccountORM).filter(AccountORM.user_id == user_id).first()
    if not acc:
        raise HTTPException(404, "Account not found")
    return acc


@app.post("/accounts/{user_id}/deposit", response_model=Account)
def deposit_account(user_id: int, payload: AccountDeposit, db: Session = Depends(get_db), current_user: UserORM = Depends(jwt_required)):
    # Only allow deposits to the authenticated user's account
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot deposit to other user's account")
    acc = db.query(AccountORM).filter(AccountORM.user_id == user_id).first()
    if not acc:
        user = db.query(UserORM).filter(UserORM.id == user_id).first()
        if not user:
            raise HTTPException(404, "User not found")
        acc = AccountORM(user_id=user_id, balance=0)
        db.add(acc)
        db.flush()
    from decimal import Decimal
    if acc.balance is None:
        acc.balance = 0
    acc.balance = acc.balance + Decimal(payload.amount)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


# JWT error handlers (FastAPI equivalents of Flask-JWT-Extended callbacks)
@app.exception_handler(JWTExpiredError)
async def expired_token_callback(request, exc: JWTExpiredError):
    return FastJSONResponse(
        status_code=_status.HTTP_401_UNAUTHORIZED,
        content={"message": "The token has expired.", "error": "token_expired"},
    )


@app.exception_handler(JWTInvalidError)
async def invalid_token_callback(request, exc: JWTInvalidError):
    return FastJSONResponse(
        status_code=_status.HTTP_401_UNAUTHORIZED,
        content={"message": "Signature verification failed.", "error": "invalid_token"},
    )


@app.exception_handler(JWTMissingError)
async def missing_token_callback(request, exc: JWTMissingError):
    return FastJSONResponse(
        status_code=_status.HTTP_401_UNAUTHORIZED,
        content={
            "description": "Request does not contain an access token.",
            "error": "authorization_required",
        },
    )