from django.contrib.auth import get_user_model
from model_bakery.recipe import Recipe
from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker

User = get_user_model()


class TestSetUp(APITestCase):

    def setUp(self):
        self.fake = Faker(locale="fa_IR")

        self.user_receipt = Recipe(
            User,
            first_name=self.fake.first_name(),
            last_name=self.fake.first_name(),
            mobile_number=f'09{self.fake.random_number(9)}',
            email=self.fake.email()
        )

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
