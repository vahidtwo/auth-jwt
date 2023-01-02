import logging
import random

import jwt
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_yasg import openapi
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import User, OTP
from account.serializers import (
    LoginSerializer,
    LogoutSerializer,
    ConfirmOTPSerializer,
)
from account.task import send_otp_verification

logger = logging.getLogger(__name__)


class RequestOTP(views.APIView):
    logger = logger
    mobile_number_config = openapi.Parameter(
        "mobile_number",
        in_=openapi.IN_QUERY,
        description="mobile_number",
        type=openapi.TYPE_STRING,
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="mobile_number",
                description="mobile_number",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def get(self, request):
        mobile_number = request.GET.get("mobile_number")
        get_object_or_404(User, mobile_number=mobile_number)
        otp = OTP.objects.filter(mobile_number=mobile_number)
        if not otp.exists() or (otp.exists() and otp.first().expired):
            otp = OTP.objects.create(
                mobile_number=mobile_number, otp=str(random.randint(1111, 9999))
            )
            message = "OTP send successfully"
        else:
            otp = otp.first()
            message = "OTP sent if you dont receive please try 2 min later"
        send_otp_verification.delay(otp.otp)
        return Response({"message": message})


class VerifyEmail(views.APIView):
    logger = logger

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="token",
                description="access_token",
                required=False,
                type=str,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified_email:
                user.is_verified_email = True
                user.save()
            return Response(
                {"message": "Successfully activated"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"message": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class VerifyMobile(generics.GenericAPIView):
    logger = logger
    serializer_class = ConfirmOTPSerializer

    def post(self, request):
        mobile_number = request.data.get("mobile_number")
        user = User.objects.get(mobile_number=mobile_number)
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.matched()

        if not user.is_verified_mobile:
            user.is_verified_mobile = True
            user.save()
        return Response(
            {"message": "Successfully activated"}, status=status.HTTP_200_OK
        )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    logger = logger

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    logger = logger
    serializer_class = LogoutSerializer

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
