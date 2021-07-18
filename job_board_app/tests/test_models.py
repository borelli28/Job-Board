from datetime import datetime
from django.test import TestCase
from job_board_app.models import User, Jobs

class TestUserModel(TestCase):

    def setUp(self):
        # create user instance to test views from
        self.user = User.objects.create(email="test@test", password="123345678")

    def test_user_field(self):
        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.password, str)
