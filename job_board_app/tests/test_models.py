from datetime import datetime
from django.test import TestCase
from job_board_app.models import User, Jobs

class TestUserModel(TestCase):

    def setUp(self):
        # create user instance
        self.user = User.objects.create(username="testusername", password="123345678")

    # check attributes are the correct type
    def test_user_field(self):
        self.assertIsInstance(self.user.username, str, "User name is not String type")
        self.assertIsInstance(self.user.password, str, "User password is not String type")

class TestJobsModel(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testusername", password="123345678")
        self.job = Jobs.objects.create(status="Applied", title="Software Dev", company="Some Tech Co.",
        url="https://borelliarmando.com/", location="Austin, TX", user_jobs=self.user)

    def test_jobs_field(self):
        # check attributes are the correct type
        self.assertIsInstance(self.job.status, str, "Job status is not String type")
        self.assertIsInstance(self.job.title, str, "Job title is not String type")
        self.assertIsInstance(self.job.company, str, "Job company is not String type")
        self.assertIsInstance(self.job.url, str, "Job url is not String type")
        self.assertIsInstance(self.job.location, str, "Job location is not String type")
        self.assertIsInstance(self.job.user_jobs, User, "Job user_jobs ForeignKey attribute is not User type")
