import os

# Django settings for PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "mydb"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "password"),
        "HOST": os.getenv(
            "DATABASE_HOST", "db"
        ),  # Service name in Docker Compose
        "PORT": os.getenv("DATABASE_PORT", "5432"),
    }
}
