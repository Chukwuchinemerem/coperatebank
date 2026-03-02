import os
from pathlib import Path
import dj_database_url
from dotenv.main import load_dotenv

# Superuser credentials for non-interactive creation (used by custom management command)
DJANGO_SUPERUSER_USERNAME = os.getenv("DJANGO_SUPERUSER_USERNAME")
DJANGO_SUPERUSER_EMAIL = os.getenv("DJANGO_SUPERUSER_EMAIL")
DJANGO_SUPERUSER_PASSWORD = os.getenv("DJANGO_SUPERUSER_PASSWORD")

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'replace_this_with_a_real_secret_key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = [
    'coperatebank.onrender.com',
    'www.coperatebank.onrender.com',
    'www.cooperatefinance.com',
    'cooperatefinance.com',
    '127.0.0.1',
    'primepips-opmv.onrender.com',
    'www.cooperativefinancebank.onrender.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres'):
    DATABASES = {
        'default': dj_database_url.config(
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
            conn_max_age=600
        )
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
    ('de', 'German'),
    ('ar', 'Arabic'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -------------------
# Media / Render Disk Setup
# -------------------

# Render Disk path
RENDER_DISK_PATH = '/disk/media/'

# --- Commented out to prevent build failure ---
# if not os.path.exists(RENDER_DISK_PATH):
#     os.makedirs(RENDER_DISK_PATH)

# Use Render Disk for media files if DEBUG is False (production)
if not DEBUG:
    MEDIA_ROOT = RENDER_DISK_PATH
    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # Local / Debug fallback
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# Cloudinary media storage (for Render free tier and production)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Cloudinary (fallback / optional)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'dj8nqreta'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '984696234216511'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', 'h9gjs1h9J1fvjascOFFOZMW7q08'),
}


# Redirect to dashboard after login
LOGIN_REDIRECT_URL = '/dashboard/'

# -------------------
# Runtime Disk Folder Creation
# -------------------
# Create /disk/media at runtime to ensure folder exists
# THIS WILL ONLY RUN WHEN APP IS LIVE, NOT DURING BUILD
if not DEBUG:
    try:
        from pathlib import Path
        disk_path = Path(RENDER_DISK_PATH)
        disk_path.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass  # If disk isn't mounted yet, ignore error at startup
