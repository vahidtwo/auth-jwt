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

    def test_get_profile(self):
        url = reverse("profile")
        self.login_user()
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['data']['first_name'], self.user.first_name)

    def test_update_profile(self):
        url = reverse("profile")
        payload = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "mobile_number": f'09{self.fake.random_number(9)}',
            "email": self.fake.email()
        }
        self.login_user()
        self.user.is_verified_email = True
        self.user.is_verified_mobile = True
        self.user.save()
        res = self.client.put(url, data=payload, type='json')
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(payload['first_name'], self.user.first_name)
        self.assertEqual(payload['last_name'], self.user.last_name)
        self.assertEqual(payload['mobile_number'], self.user.mobile_number)
        self.assertEqual(payload['email'], self.user.email)
        self.assertEqual(self.user.is_verified_mobile, False)
        self.assertEqual(self.user.is_verified_email, False)
