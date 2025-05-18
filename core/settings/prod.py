from .base import *

DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

if not APP_ENC_KEY or not APP_ENC_VEC:
    raise ValueError("APP_ENC_KEY and APP_ENC_VEC must be set in production")

if not all([EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    raise ValueError("Email settings are not properly configured for production")
