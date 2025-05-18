from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.controllers.auth import (
    ForgotPasswordRequestView,
    LoginView,
    RegisterOtpView,
    RegisterStudentView,
    RegisterTeacherView,
    ResetPasswordInAppRequestView,
    ResetPasswordRequestView,
    SignupView,
    VerifyOtpView,
)

urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path("signup", SignupView.as_view(), name="signup"),
    path(
        "register/student", RegisterStudentView.as_view(), name="student_registration"
    ),
    path("register/teacher", RegisterTeacherView.as_view(), name="teacher_registration"),
    path("signup/resend-otp", RegisterOtpView.as_view(), name="register-otp"),
    path("signup/verify-otp", VerifyOtpView.as_view(), name="verify-otp"),
    path("token/refresh", TokenRefreshView.as_view()),
    path(
        "password/forgot", ForgotPasswordRequestView.as_view(), name="forgot-password"
    ),
    path("password/change", ResetPasswordRequestView.as_view(), name="change-password"),
    path(
        "password/in-app/change",
        ResetPasswordInAppRequestView.as_view(),
        name="change-password-in-app",
    ),
]
