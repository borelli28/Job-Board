from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from job_board_app.models import User, Jobs
import json

class TestViews(TestCase):

    def setUp(self):
        # create user instance to test views from
        User.objects.create(email="test@test", password="123")
        user = User.objects.get(id=1)

        # create a job instance for testing purposes
        job = Jobs.objects.create(status="Applied", title="Software Dev", company="Cheap Labor Inc.", url="https://borelliarmando.com/", location="Austin, TX", user_jobs=user)

        self.client = Client()

        self.index_url = reverse("index")
        self.jobs_url = reverse("render_jobs")
        self.search_job_url = reverse("job_search_logic")

    def test_index_view_get(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)

    def test_jobs_view_get(self):
        response = self.client.get(self.jobs_url)
        self.assertEquals(response.status_code, 200) # test that method returns an OK server response
        self.assertTemplateUsed(response, 'jobs.html')  # test that method renders the right template

    def test_search_job_view_get(self):
        response = self.client.get(self.search_job_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')

        # test API by checking server response to POST is OK
        response_post = self.client.post(self.search_job_url, {
            "what": "Software Dev",
            "where": "Austin"
        })
        self.assertEquals(response.status_code, 200)
