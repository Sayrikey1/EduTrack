from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False

if not APP_ENC_KEY or not APP_ENC_VEC:
    # fallback for dev
    APP_ENC_KEY = "8c6110e6d6834af6be63a5f713ce3d22"
    APP_ENC_VEC = "902f2e4d5d0246a9"
