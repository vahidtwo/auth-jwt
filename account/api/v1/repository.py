from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import smart_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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
