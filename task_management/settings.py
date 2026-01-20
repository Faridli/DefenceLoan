from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# =======================
# Security & Debug
# =======================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
# ALLOWED_HOSTS = [] 
# ALLOWED_HOSTS = ['.onrender.com']   
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com',
]

# =======================
# Installed Apps
# =======================
INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'debug_toolbar',
    'widget_tweaks',

    # Local apps
    'tasks',    
    'users',    
    'core',    
]



# =======================
# Custom User Model
# =======================
AUTH_USER_MODEL = 'tasks.User'  # 'tasks' হলো আপনার app name, 'User' হলো model name
# AUTH_USER_MODEL = 'users.User'


# =======================
# Middleware
# =======================
MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",  # should be first for debug_toolbar
    'django.middleware.security.SecurityMiddleware', 
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ⭐ এখানে
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# =======================
# TEMPLATES 
# ======================= 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # global templates (optional)
        'APP_DIRS': True,  # ⭐ খুবই গুরুত্বপূর্ণ
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

# =======================
# URL & WSGI
# =======================
ROOT_URLCONF = 'task_management.urls'
WSGI_APPLICATION = 'task_management.wsgi.application'

# =======================
# Database (SQLite via env)
# =======================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': BASE_DIR / config('DB_NAME', default='db.sqlite3'),
    }
}

# =======================
# Password Validators
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =======================
# Internationalization
# =======================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =======================
# Static & Media
# =======================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] 
STATIC_ROOT = BASE_DIR / 'staticfiles'  
# WhiteNoise gzip & cache
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# Email Configuration via .env
# =======================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

FRONTEND_URL = 'http://127.0.0.1:8000' 

# 'https://loan.render'

# SSLCOMMERZ credentials
SSLCOMMERZ_STORE_ID = config('SSLCOMMERZ_STORE_ID')
SSLCOMMERZ_STORE_PASS = config('SSLCOMMERZ_STORE_PASS')
SSLCOMMERZ_URL = config('SSLCOMMERZ_URL')



# import os

# TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
# # TWILIO_PHONE = os.getenv("TWILIO_PHONE") 
# TWILIO_VERIFY_SID= config("TWILIO_VERIFY_SID")

# login এর জন্য URL ঠিক করুন
LOGIN_URL = 'login_user'        # এখানে আমরা urls.py তে নাম ব্যবহার করব
LOGIN_REDIRECT_URL = '/tasks/dashboard/'  # লগইন হয়ে গেলে কোথায় যাবে
LOGOUT_REDIRECT_URL = '/logout/'         # লগআউট হলে কোথায় যাবে

