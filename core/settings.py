from logging import DEBUG
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
# SECURITY
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-change-me-in-production"
)

if DEBUG:
    # Обычное хранилище: Django просто ищет файлы в папках static
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    # Хранилище для продакшена (Render/Heroku): сжатие и кэширование
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


ALLOWED_HOSTS = ["*", ".onrender.com"]


# ======================
# APPS
# ======================
INSTALLED_APPS = [
    # 1. Сначала хранилище
    "cloudinary_storage", 
    
    # 2. Потом стандартная статика
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3. Твои приложения
    "edits",
    "theme",
    "tailwind",
    "django_browser_reload",
    "cloudinary",
]



# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "core.urls"


# ======================
# TEMPLATES
# ======================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "core.wsgi.application"


# ======================
# DATABASE
# ======================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ======================
# CLOUDINARY STORAGE (ВМЕСТО MEDIA_ROOT)
# ======================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("dtdam7g1h"),
    "API_KEY": os.environ.get("217115362956957"),
    "API_SECRET": os.environ.get("F2aLRyDd6r_i9hug2GjQNmilOrI"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


# ======================
# PASSWORD VALIDATION
# ======================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ======================
# STATIC FILES
# ======================
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "theme/static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ======================
# MEDIA URL (для ссылок)
# ======================
MEDIA_URL = "/media/"


# ======================
# TAILWIND
# ======================
TAILWIND_APP_NAME = "theme"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ======================
# AUTH
# ======================
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
