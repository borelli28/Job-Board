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
        self.tracker_app_url = reverse("render_tracker_app")
        self.set_job_url = reverse("save_job_info")
        self.go_to_job_url = reverse("go_to_job")
        self.viewed_jobs_handler_url = reverse("viewed_job_handler", args=[job.id])

    def test_index_view(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)

    def test_jobs_view(self):
        response = self.client.get(self.jobs_url)
        self.assertEquals(response.status_code, 200) # test that method returns an OK server response
        self.assertTemplateUsed(response, 'jobs.html')  # test that method renders the right template

    def test_search_job_view(self):
        response = self.client.get(self.search_job_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'jobs.html')

    def test_tracker_app_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.get(self.tracker_app_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'tracker_app.html')

    def test_set_job_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.post(self.set_job_url, {
            "title": "Software Tester",
            "company": "Some Company",
            "location": "Dallas, TX",
            "url": "https://www.youtube.com/watch?v=hA_VxnxCHbo&list=PLbpAWbHbi5rMF2j5n6imm0enrSD9eQUaM&index=3"
        })
        self.assertEquals(response.status_code, 302) # redirect() returns a 302 code instead of a 200
        job = Jobs.objects.last()
        self.assertEquals(job.location, "Dallas, TX") # checks that the object posted is being saved

    def test_go_to_job_view(self):
        session = self.client.session
        session['url'] = "https://www.youtube.com/watch?v=hA_VxnxCHbo&list=PLbpAWbHbi5rMF2j5n6imm0enrSD9eQUaM&index=3"
        session.save()

        response = self.client.get(self.go_to_job_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'go_to_job.html')

    def test_viewed_jobs_handler_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.get(self.viewed_jobs_handler_url)
        self.assertEquals(response.status_code, 302)

        # check that when post is "yes" the job status is changed to Applied
        response = self.client.post(self.viewed_jobs_handler_url, {
            "applied?": "yes"
        })
        job = Jobs.objects.last()
        self.assertEquals(job.status, "Applied")

        # if the post is "no" then the job should be deleted, test case needs to return None
        response = self.client.post(self.viewed_jobs_handler_url, {
            "applied?": "no"
        })
        job = Jobs.objects.last()
        self.assertIsNone(job, "viewed_jobs_handler did not delete the job when POST is 'no' ")
