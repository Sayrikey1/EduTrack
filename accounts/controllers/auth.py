from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from accounts.models import UserTypes
from accounts.serializers.auth import (
    ForgotPasswordRequestSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ResendOtpSerializer,
    ResetPasswordInAppRequestSerializer,
    ResetPasswordRequestSerializer,
    SignupSerializer,
    VerifyOtpSerializer,
)
from accounts.services.auth import AuthService
from services.util import CustomApiRequestProcessorBase, user_type_required


class LoginView(TokenObtainPairView, CustomApiRequestProcessorBase):
    permission_classes = []
    authentication_classes = []
    serializer_class = LoginSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Login enpoint for users.",
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "access": {"type": "string"},
                    "refresh": {"type": "string"},
                },
            },
            400: {"type": "object", "properties": {"error": {"type": "string"}}},
        },
    )
    @method_decorator(ratelimit(key="ip", rate="3/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.login)


class SignupView(CreateAPIView, CustomApiRequestProcessorBase):
    authentication_classes = []
    permission_classes = []
    serializer_class = SignupSerializer

    @extend_schema(tags=["Auth"])
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.log_register)


class RegisterStudentView(CreateAPIView, CustomApiRequestProcessorBase):
    authentication_classes = []
    permission_classes = []
    serializer_class = RegistrationSerializer

    @extend_schema(tags=["Auth"])
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(
            request, service.register, register_type=UserTypes.student
        )


class RegisterTeacherView(CreateAPIView, CustomApiRequestProcessorBase):
    authentication_classes = []
    permission_classes = []
    serializer_class = RegistrationSerializer

    @extend_schema(tags=["Auth"])
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(
            request, service.register, register_type=UserTypes.teacher
        )


class RegisterOtpView(CreateAPIView, CustomApiRequestProcessorBase):
    authentication_classes = []
    permission_classes = []
    serializer_class = ResendOtpSerializer

    @extend_schema(tags=["Auth"])
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.resend_registration_otp)


class VerifyOtpView(CreateAPIView, CustomApiRequestProcessorBase):
    authentication_classes = []
    permission_classes = []
    serializer_class = VerifyOtpSerializer

    @extend_schema(tags=["Auth"])
    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.verify_register_otp)


class ResetPasswordRequestView(CreateAPIView, CustomApiRequestProcessorBase):
    serializer_class = ResetPasswordRequestSerializer
    authentication_classes = []
    permission_classes = []

    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.reset_password)


class ResetPasswordInAppRequestView(CreateAPIView, CustomApiRequestProcessorBase):
    serializer_class = ResetPasswordInAppRequestSerializer
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.reset_password_in_app)


class ForgotPasswordRequestView(CreateAPIView, CustomApiRequestProcessorBase):
    serializer_class = ForgotPasswordRequestSerializer

    permission_classes = []
    authentication_classes = []

    @method_decorator(ratelimit(key="ip", rate="5/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.request_password_reset)


class ValidateAuthenticatorOTPView(CreateAPIView, CustomApiRequestProcessorBase):
    permission_classes = []
    authentication_classes = []

    @method_decorator(ratelimit(key="ip", rate="3/m"))
    def post(self, request, *args, **kwargs):
        service = AuthService(request)
        return self.process_request(request, service.validate_authenticator_otp)
