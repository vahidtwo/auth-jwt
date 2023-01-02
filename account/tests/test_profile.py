from unittest import mock

from django.urls import reverse

from .test_setup import TestSetUp
from ..api.v1.repository import URLForgetPassword


class TestProfileAPIS(TestSetUp):
    def setUp(self):
        super(TestProfileAPIS, self).setUp()
        self.user = self.user_receipt.make()
        self.user.set_password(self.user.email[:8])
        self.user.save()

    def test_password_reset(self):
        with mock.patch("account.api.v1.profile.URLForgetPassword.create_token"):
            res = self.client.post(
                reverse("request-reset-email"),
                {"email": self.user.email},
                format="json",
            )
            self.assertEqual(res.status_code, 200)
        abs_url = URLForgetPassword.create_token(self.user, "127.0.0.1")
        *_, uidb64, token = abs_url.split("/")
        res = self.client.get(reverse("password-reset-confirm", args=(uidb64, token)))
        self.assertEqual(res.status_code, 301)
        self.assertTrue("token_valid=True" in res.url)

    def test_invalid_uid_and_token_for_password_reset_confirm(self):
        uidb64, token = 'NQ', 'assafdsxzxfasdrfeware'
        res = self.client.get(reverse("password-reset-confirm", args=(uidb64, token)))
        self.assertEqual(res.status_code, 301)
        self.assertTrue("token_valid=False" in res.url)
