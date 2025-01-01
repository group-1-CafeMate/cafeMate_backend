"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
import dotenv
from celery.schedules import crontab

# Load .env file
dotenv.load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# 設置debug 生產環境要改False
DEBUG = os.getenv("DEBUG")

ALLOWED_HOSTS = [
    "cafe.urcafemate.me",
    "localhost",
    "127.0.0.1",
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # our apps
    "cafeInfo",
    "user",
    "mail",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # CorsMiddleware 必須在 CommonMiddleware 之前
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# 允許的 CORS 設定
CORS_ALLOW_ALL_ORIGINS = True  # 開放所有跨域請求（生產環境建議改為特定域名）
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
CORS_ALLOW_HEADERS = ("*", "content-type", "Origin")

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:8000",
#     "http://localhost:3000",
# ]
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = None

SESSION_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_PARTITIONED = True

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("MYSQL_NAME"),
        "USER": os.getenv("MYSQL_USER"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD"),
        "HOST": os.getenv("MYSQL_HOST"),
        "PORT": "3306",
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://redis:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# AWS 設定
AWS_REGION = "ap-northeast-1"  # 使用的 AWS 區域
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")  # IAM USER's ACCESS_KEY
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  # USER's SECRET_ACCESS_KEY
AWS_SQS_VERIFICATION_QUEUE_URL = "https://sqs.ap-northeast-1.amazonaws.com/481665090171/EmailSystemSqsStack-EmailVerificationQueue00C720A8-S96W6o7HLuQi"
AWS_SQS_NEW_PASSWORD_QUEUE_URL = "https://sqs.ap-northeast-1.amazonaws.com/481665090171/EmailSystemSqsStack-ForgotPasswordQueue5CF9634F-EbHptG23l9yG"

# Celery 設置
CELERY_BROKER_URL = (
    f"sqs://{os.getenv('AWS_ACCESS_KEY_ID')}:{os.getenv('AWS_SECRET_ACCESS_KEY')}@"
)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "region": "ap-northeast-1",  # 改為你的 AWS 區域
    "queue_name_prefix": "celery-",
}
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TRACK_STARTED = True
CELERY_BEAT_SCHEDULE = {
    "process_verification_email_every_minute": {
        "task": "mail.tasks.process_verification_email_from_sqs",
        "schedule": crontab(minute="*"),  # 每分鐘執行
    },
    "process_forgot_email_every_minute": {
        "task": "mail.tasks.process_forgot_email_from_sqs",
        "schedule": crontab(minute="*"),  # 每分鐘執行
    },
}

"""
啟用後，當任務啟動時，會將任務的狀態從 PENDING 更新為 STARTED。
這對於監控任務進度很有用，可以更準確地追踪正在執行的任務。
"""
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 分鐘
"""
為每個任務設置執行的時間上限，這裡是 30 分鐘。
如果任務在 30 分鐘內未完成，Celery 會強制終止該任務。
適用
"""

# Google Gmail service
SITE_URL = "http://127.0.0.1:8000"  # 網站設定 本地端用
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587  # TLS 通訊埠號
EMAIL_USE_TLS = True  # 開啟TLS(傳輸層安全性)
# 寄件人的信箱的帳號
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
# 寄件人的信箱的應用程式密碼
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 日誌配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/mail.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "mail": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "zh-hant"  # 繁體中文

TIME_ZONE = "Asia/Taipei"

USE_I18N = True

USE_TZ = True

MEDIA_URL = "media/"
# MEDIA_ROOT = os.path.join(BASE_DIR, "app/media")
MEDIA_ROOT = "/app/media"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
