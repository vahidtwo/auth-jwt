import random
from account.task import send_otp_verification, send_url_verification

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import smart_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import OTP

User = get_user_model()


class URLForgetPassword:
    @staticmethod
    def create_token(user, current_site):
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        relative_link = reverse(
            "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        abs_url = "http://" + current_site + relative_link
        return abs_url

    @staticmethod
    def check_token(uidb64, token):
        try:
            _id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=_id)
            return PasswordResetTokenGenerator().check_token(user, token)
        except (DjangoUnicodeDecodeError, UnboundLocalError, User.DoesNotExist) as identifier:
            return False


class SendVerification:
    @staticmethod
    def send(*args):
        raise NotImplementedError()


class SendOTP(SendVerification):
    @staticmethod
    def send(mobile_number):
        otp = OTP.objects.filter(mobile_number=mobile_number)
        if not otp.exists() or (otp.exists() and otp.first().expired):
            otp = OTP.objects.create(
                mobile_number=mobile_number, otp=str(random.randint(1111, 9999))
            )
            message = "OTP send successfully"
            send_otp_verification.delay(otp.otp)
        else:
            message = "OTP sent if you dont receive please try 2 min later"
        return message
    # implement
    # @staticmethod
    # def send(mobile_number):
    #     cash.set(mobile_number, random.randint(1111,9999))


class SendVerifyEmail(SendVerification):
    @staticmethod
    def send(request, user, new_email=None):
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse("email-verify")
        abs_url = "http://" + current_site + relative_link + "?token=" + str(token)
        send_url_verification.delay(abs_url)
        return 'Email Verification code sent'
