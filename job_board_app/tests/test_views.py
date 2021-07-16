from django.test import TestCase, Client
from django.urls import reverse
from job_board_app.models import *
import json

class TestViews(TestCase):

    def setUp(self):
        # create user instance to test views from
        User.objects.create(email="test@test", password="123")

        self.client = Client()
        self.index_url = reverse("index")

    def test_index_view_get(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)
        # self.assertTemplateUsed(response, 'job_board_app/')
