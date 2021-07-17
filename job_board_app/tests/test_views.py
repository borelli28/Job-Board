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
        self.user = user

        session = self.client.session
        session['userid'] = user.id
        session.save()

        # create a job instance for testing purposes
        job = Jobs.objects.create(status="Applied", title="Software Dev", company="Cheap Labor Inc.", url="https://borelliarmando.com/", location="Austin, TX", user_jobs=user)
        self.job = job

        self.client = Client()

        # FORMAT: self.[method_name]_url = reverse("[url_name]", [url_parameter])
        self.index_url = reverse("index")
        self.jobs_url = reverse("render_jobs")
        self.search_job_url = reverse("job_search_logic")
        self.tracker_app_url = reverse("render_tracker_app")
        self.set_job_url = reverse("save_job_info")
        self.go_to_job_url = reverse("go_to_job")
        self.viewed_jobs_handler_url = reverse("viewed_job_handler", args=[job.id])
        self.edit_job_url = reverse("edit_job_form", args=[job.id])
        self.update_job_url = reverse("update_job_logic", args=[job.id])
        self.delete_job_url = reverse("delete_job", args=[job.id])
        self.job_note_url = reverse("render_job_note", args=[job.id])

    # FORMAT: test_[method_name]_view(self)
    def test_index_view(self):
        response = self.client.get(self.index_url)
        self.assertEquals(response.status_code, 200)    # checks that page is rendering
        self.assertEquals(response.content, b"hello", "index() method did not return 'hello' response")

    def test_jobs_view(self):
        response = self.client.get(self.jobs_url)
        self.assertEquals(response.status_code, 200) # test that method returns an OK server response(page renders!)
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

        # check that view redirect to another URL
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

    # render the edit_job_page          update_job_url
    def test_edit_job_view(self):

        response = self.client.get(self.edit_job_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_job.html')

        # check that job passed(as an id) is the one returned in context
        self.assertEquals(response.context["job"], self.job)

    # check that all job attributes were updated
    def test_update_job_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.post(self.update_job_url, {
            "status": "Interviewing",
            "title": "New job title",
            "company": "New company name",
            "location": "Middle of nowhere"
        })
        self.assertEquals(response.status_code, 302)   # checks that the method redirects succesfully

        job = Jobs.objects.last()

        # check that method is updating all the attributes
        self.assertEquals(job.status, "Interviewing", "Job status was not updated")
        self.assertEquals(job.title, "New job title", "Job title was not updated")
        self.assertEquals(job.company, "New company name", "Job company was not updated")
        # TODO: uncomment the test below when the location is added to edit form
        # self.assertEquals(job.location, "Middle of nowhere", "Job location was not updated")

        # test the code used in the method to validate that the logged user can
        self.assertEquals(job.user_jobs, self.user, "The user that create the job instance don't match the logged user")

    # check that job is deleted *IF* the logged user was the one that created the job instance
    def test_delete_job_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        # validate the method used to check that user has the authorization to delete the job
        self.assertTrue(self.job.user_jobs == self.user, "Logged user is not the one that created the job instance")

        response = self.client.delete(self.delete_job_url)
        self.assertEquals(response.status_code, 302)   # checks that the method redirects succesfully

        # make sure that the job was deleted
        job = Jobs.objects.last()
        self.assertIsNone(job, "Job was not deleted")

    def test_job_note_view(self):
        session = self.client.session
        session['userid'] = 1
        session.save()

        # validate the method used to check that user has the authorization to view the job note
        self.assertTrue(self.job.user_jobs == self.user, "Logged user is not the one that created the job instance")

        response = self.client.get(self.job_note_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'note.html')

        # check that the job in context is the same job selected by the user
        self.assertTrue(response.context["job"] == self.job, "Job passed as parameter is not the same one in context")

        # check that the note in context is the same note of the job instance passed
        self.assertTrue(response.context["note"] == self.job.note, "Note in context is not the same one from the job passed")
