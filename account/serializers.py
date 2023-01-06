from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.utils.encoding import (
    force_str,
)
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from core.validator import mobile_number_validation
from .api.v1.repository import SendOTP, SendVerifyEmail
from .models import User, OTP


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["email", "mobile_number", "password", "first_name", "last_name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    default_error_messages = {"e_m_null": "mobile number or email must be send"}
    email = serializers.EmailField(required=False)
    mobile_number = serializers.CharField(
        validators=[mobile_number_validation], required=False
    )

    class Meta:
        model = User
        fields = ["email", "password", "tokens", "mobile_number"]

    def validate(self, attrs):
        email = attrs.get("email")
        mobile_number = attrs.get("mobile_number")
        password = attrs.get("password")
        if email is not None:
            user = auth.authenticate(email=email, password=password)
        elif mobile_number is not None:
            _user = get_object_or_404(User, mobile_number=mobile_number)
            user = auth.authenticate(email=_user.email, password=password)
        else:
            raise self.fail("e_m_null")

        if not user:
            raise AuthenticationFailed("Invalid credentials, try again")
        if email is not None and user.is_verified_email is False:
            raise AuthenticationFailed("Email is not verified")
        elif mobile_number is not None and user.is_verified_mobile is False:
            raise AuthenticationFailed("Mobile is not verified")
        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin")

        return {
            "email": user.email,
            "mobile_number": user.mobile_number,
            "tokens": user.tokens,
        }


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ["email"]


class SetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    refresh = serializers.CharField()
    default_error_messages = {"bad_token": "Token is expired or invalid"}

    class Meta:
        model = User
        fields = ("password", "refresh")

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def update(self, instance, validated_data):
        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


class ForgetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            token = attrs.get("token")
            uidb64 = attrs.get("uidb64")

            _id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("The reset link is invalid", 401)
            user.set_password(password)
            user.save()
            RefreshToken(user.tokens["access"]).blacklist()

            return user
        except Exception as e:
            raise AuthenticationFailed("The reset link is invalid", 401)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {"bad_token": "Token is expired or invalid"}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")


class ConfirmOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=4)
    mobile_number = serializers.CharField(
        max_length=14, min_length=11, validators=[mobile_number_validation]
    )

    class Meta:
        fields = ["otp", "mobile_number"]

    def validate(self, attrs):
        """
        validate input otp
        if otp is expired or otp is wrong , raised validation error
        """
        mobile_number = attrs.get("mobile_number")
        otp = attrs.get("otp")
        self.instance = OTP.objects.filter(otp=otp, mobile_number=mobile_number)
        if not self.instance.exists():
            raise serializers.ValidationError("otp not match")
        if self.instance.first().expired:  # if otp expired send error
            raise serializers.ValidationError("otp expired")

        return attrs

    def matched(self):
        """
        set this otp used
        """
        if self.instance is not None and self.instance.exists():
            obj = self.instance.first()
            obj.is_matched = True
            obj.save()
        """
        it can be implement with redis 
        """


class UserProfile(ModelSerializer):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'mobile_number', 'email')
        model = User

    def validate(self, attrs):
        email = attrs.get('email')
        mobile_number = attrs.get('mobile_number')
        if email is not None and self.instance.email != email:
            self.instance.is_verified_email = False
            SendVerifyEmail.send(self.context['request'], self.instance)
        if mobile_number is not None and self.instance.mobile_number != mobile_number:
            self.instance.is_verified_mobile = False
            SendOTP.send(mobile_number)
        self.instance.save()
        return attrs
