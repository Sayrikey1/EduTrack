from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/", include("api.urls.auth")),
    path("courses/", include("api.urls.courses")),
    path("assignments/", include("api.urls.assignments"))
    ]