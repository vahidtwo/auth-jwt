import logging
import os
import random

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet
from account.api.v1.repository import URLForgetPassword, SendOTP, SendVerifyEmail
from account.models import User, OTP
from account.serializers import (
    RegisterSerializer,
    ForgetPasswordSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer, UserProfile,
)
from account.task import send_otp_verification, send_url_verification

logger = logging.getLogger(__name__)


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get("APP_SCHEME"), "http", "https"]


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    logger = logger

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        SendOTP.send(user.mobile_number)
        SendVerifyEmail.send(request, user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    logger = logger

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get("email", "")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            current_site = get_current_site(request=request).domain
            abs_url = URLForgetPassword.create_token(user, current_site)
            print(f"password verification url is {abs_url}")
        return Response(
            {"message": "We have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    logger = logger

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get("redirect_url", "")
        if not URLForgetPassword.check_token(uidb64, token):
            if len(redirect_url) > 3:
                return CustomRedirect(redirect_url + "?token_valid=False")
            else:
                return CustomRedirect(
                    os.environ.get("FRONTEND_URL", "") + "?token_valid=False"
                )
        if redirect_url and len(redirect_url) > 3:
            return CustomRedirect(
                redirect_url
                + "?token_valid=True&message=Credentials Valid&uidb64="
                + uidb64
                + "&token="
                + token
            )
        else:
            return CustomRedirect(
                os.environ.get(
                    "FRONTEND_URL",
                    reverse("password-reset-complete")
                    + "?token_valid=True&message=Credentials Valid&uidb64="
                    + uidb64
                    + "&token="
                    + token,
                )
            )


class ForgetPasswordAPIView(generics.GenericAPIView):
    """
    set new password for requested password reset email
    """

    serializer_class = ForgetPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            {"message": "Password reset success"}, status=status.HTTP_200_OK
        )


class SetNewPasswordAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetNewPasswordSerializer
    logger = logger

    def patch(self, request):
        user = request.user
        ser = self.get_serializer(user, data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(
            {"data": user.tokens(), "message": "Password update success"},
            status=status.HTTP_200_OK,
        )


class ProfileView(GenericViewSet):
    permission_classes = (IsAuthenticated,)
    logger = logger
    serializer_class = UserProfile

    @action(detail=False, methods=['get'])
    def get_profile(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        ser = self.get_serializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"message": "profile update successfully"})
