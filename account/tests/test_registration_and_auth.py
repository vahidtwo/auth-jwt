from django.urls import reverse

from .test_setup import TestSetUp


class TestViews(TestSetUp):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        super().setUp()

    def test_user_cannot_register_with_no_data(self):
        res = self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_user_can_register_correctly(self):
        payload = {
            "first_name": self.fake.first_name(),
            "last_name": self.fake.first_name(),
            "mobile_number": f"09{self.fake.random_number(9)}",
            "email": self.fake.email(),
            "password": self.fake.email()[:8],
        }
        res = self.client.post(
            self.register_url, payload, format="json")
        self.assertEqual(res.json()['data']['email'], payload['email'])
        self.assertEqual(res.json()['data']['mobile_number'], payload['mobile_number'])
        self.assertEqual(res.json()['data']['last_name'], payload['last_name'])
        self.assertEqual(res.json()['data']['first_name'], payload['first_name'])
        self.assertEqual(res.status_code, 201)

    def test_user_cannot_login_with_unverified_email(self):
        user = self.user_receipt.make()
        user.set_password(user.email[:8])
        user.save()
        login_payload = {'email': user.email, 'password': user.email[:8]}
        res = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(res.status_code, 401)

    def test_user_cannot_login_with_unverified_mobile(self):
        user = self.user_receipt.make()
        user.set_password(user.email[:8])
        user.save()
        login_payload = {'mobile_number': user.mobile_number, 'password': user.email[:8]}
        res = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(res.status_code, 401)

    def test_user_can_login_after_email_verification(self):
        user = self.user_receipt.make()
        user.set_password(user.email[:8])
        user.save()
        login_payload = {'email': user.email, 'password': user.email[:8]}
        user.is_verified_email = True
        user.save()
        res = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(res.status_code, 200)

    def test_user_can_login_after_mobile_verification(self):
        user = self.user_receipt.make()
        user.set_password(user.email[:8])
        user.save()
        login_payload = {'mobile_number': user.mobile_number, 'password': user.email[:8]}
        user.is_verified_mobile = True
        user.save()
        res = self.client.post(self.login_url, login_payload, format="json")
        self.assertEqual(res.status_code, 200)