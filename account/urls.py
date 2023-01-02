from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from account.api.v1 import (
    RegisterView,
    LogoutAPIView,
    ForgetPasswordAPIView,
    VerifyEmail,
    LoginAPIView,
    PasswordTokenCheckAPI,
    RequestPasswordResetEmail,
    RequestOTP,
    VerifyMobile, SetNewPasswordAPIView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginAPIView.as_view(), name="login"),
    path("logout", LogoutAPIView.as_view(), name="logout"),
    path("request-otp", RequestOTP.as_view(), name="request_otp"),
    path("mobile-verify", VerifyMobile.as_view(), name="mobile-verify"),
    path("email-verify", VerifyEmail.as_view(), name="email-verify"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "request-reset-password",
        RequestPasswordResetEmail.as_view(),
        name="request-reset-email",
    ),
    path(
        "password-reset/<uidb64>/<token>",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password-reset-complete",
        ForgetPasswordAPIView.as_view(),
        name="password-reset-complete",
    ),
    path("new-password", SetNewPasswordAPIView.as_view(), name="set_new_password"),
]
