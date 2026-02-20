import os
from pathlib import Path
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# На Render лучше добавить переменную SECRET_KEY в настройках
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-a7ru=82$#4@^56dn7i45_wytk@%(f6j@p^q!$^jf8ty++az4kz')

# SECURITY WARNING: don't run with debug turned on in production!
# На сервере автоматически станет False, если добавишь переменную DEBUG=False
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Обязательно разрешаем хосты, чтобы сайт открылся
ALLOWED_HOSTS = ['*', '.onrender.com']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Твои приложения
    'cloudinary_storage',
    'cloudinary',
    'edits',
    'theme',
    'tailwind',
    'django_browser_reload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Для работы статики (CSS) на Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# База данных (Neon PostgreSQL)
# Если переменная DATABASE_URL не найдена (например, локально), будет ошибка, 
# поэтому мы оставили твою ссылку как дефолтную.
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://neondb_owner:npg_RF5YWD6Akovu@ep-mute-snow-airowrpf-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require',
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC & MEDIA FILES ---

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Пути к статике твоего Tailwind приложения
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'theme/static'),
]

# Хранение статики через WhiteNoise (сжатие для скорости)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Настройки для Cloudinary (Медиа файлы)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'db9tyi4vy',
    'API_KEY': '845546929983293',
    'API_SECRET': 'YIUjBGwtoQbI1HT4MnarkAbnics'
}

MEDIA_URL = '/media/'
# Это заставляет Django слать видео и фото в облако, а не на диск Render
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.VideoMediaCloudinaryStorage'

# Tailwind настройки
TAILWIND_APP_NAME = 'theme'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
