import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load variables from a local .env file if present (works both locally and in Docker)
load_dotenv()

# Debug/behavior flags
PROPAGATE_EXCEPTIONS: bool = True
DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

# API / OpenAPI metadata
API_TITLE: str = os.getenv("API_TITLE", "Expense Tracker API")
API_VERSION: str = os.getenv("API_VERSION", "v1")
OPENAPI_VERSION: str = os.getenv("OPENAPI_VERSION", "3.0.3")
OPENAPI_URL_PREFIX: str = os.getenv("OPENAPI_URL_PREFIX", "/")  # e.g. "/" or "/api/"
OPENAPI_SWAGGER_UI_PATH: str = os.getenv("OPENAPI_SWAGGER_UI_PATH", "/docs")
OPENAPI_SWAGGER_UI_URL: str = os.getenv("OPENAPI_SWAGGER_UI_URL", "https://cdn.jsdelivr.net/npm/swagger-ui-dist")
REDOC_PATH: str = os.getenv("REDOC_PATH", "/redoc")

# Database URL builder from environment variables

def _build_database_url() -> str:
    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit
    if os.getenv("POSTGRES_PASSWORD"):
        # URL-encode user & password to safely handle special characters
        user = quote_plus(os.getenv("POSTGRES_USER", "postgres"))
        password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
        host = os.getenv("POSTGRES_HOST", "db")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "LAB3")
        return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
    return "sqlite:///./app.db"

DATABASE_URL: str = _build_database_url()

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 