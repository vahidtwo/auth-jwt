import logging
import os
import random

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.encoding import smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import User, OTP
from account.serializers import (
    RegisterSerializer,
    ForgetPasswordSerializer,
    ResetPasswordEmailRequestSerializer,
    SetNewPasswordSerializer,
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
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse("email-verify")
        abs_url = "http://" + current_site + relative_link + "?token=" + str(token)
        otp = OTP.objects.create(
            mobile_number=user.mobile_number, otp=str(random.randint(1111, 9999))
        )
        send_otp_verification.delay(otp.otp)
        send_url_verification.delay(abs_url)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get("email", "")

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relative_link = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            abs_url = "http://" + current_site + relative_link
            print(f"password verification url is {abs_url}")
        return Response(
            {"message": "We have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer
    logger = logger

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get("redirect_url")
        try:
            _id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
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

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + "?token_valid=False")

            except UnboundLocalError as e:

                return Response(
                    {"error": "Token is not valid, please request a new one"},
                    status=status.HTTP_400_BAD_REQUEST,
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
