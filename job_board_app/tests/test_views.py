from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from job_board_app.models import *
import bcrypt
import json

class TestViews(TestCase):

    def setUp(self):
        # create user instance to test views from
        User.objects.create(username="testuser", password="12345678")
        user = User.objects.get(id=User.objects.last().id)
        self.user = user

        session = self.client.session
        session['userid'] = user.id
        session.save()

        # create a job instance for testing purposes
        self.job = Jobs.objects.create(status="Applied", title="Software Dev", company="Some Tech Co.",
        url="https://borelliarmando.com/", location="Austin, TX", user_jobs=user)

        self.client = Client()

        # FORMAT: self.[method_name]_url = reverse("[url_name]", [url_parameter])
        self.register_url = reverse("register")
        self.register_user_url = reverse("register_user")
        self.login_url = reverse("login")
        self.log_user_url = reverse("log_user")
        self.jobs_url = reverse("render_jobs")
        self.search_job_url = reverse("job_search_logic")
        self.tracker_app_url = reverse("render_tracker_app")
        self.set_job_url = reverse("save_job_info")
        self.go_to_job_url = reverse("go_to_job")
        self.viewed_jobs_handler_url = reverse("viewed_job_handler", args=[self.job.id])
        self.edit_job_url = reverse("edit_job_form", args=[self.job.id])
        self.update_job_url = reverse("update_job_logic", args=[self.job.id])
        self.delete_job_url = reverse("delete_job", args=[self.job.id])
        self.job_note_url = reverse("render_job_note", args=[self.job.id])
        self.update_note_url = reverse("update_job_note", args=[self.job.id])
        self.new_job_url = reverse("new_job_form")
        self.add_job_url = reverse("add_job")

    # FORMAT: test_[method_name]_view(self)
    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'register.html', "Method render the wrong template")

    def test_register_user_view(self):
        # if POST request was succesful
        response = self.client.post(self.register_user_url, {
            "username": "testusername1001012349",
            "password": "somepassword",
            "confirm_password": "somepassword"
        })
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code") # redirect() returns a 302 code instead of a 200
        self.assertEquals(response.url, "/jobs", "Method redirected to wrong URL")
        new_user = User.objects.last()
        self.assertEquals(new_user.username, "testusername1001012349", "Username passed in POST req is not the same being saved in the DB")
        self.assertNotEqual(new_user.password, "somepassword", "Literal user password is being saved in the DB(user password is not being hashed)") # checks that password is being hashed with bcrypt as we are not saving the literal password in the DB

        # test if POST request is invalid(validation errors found)
        response = self.client.post(self.register_user_url, {
            "username": "us",
            "password": "some",
            "confirm_password": "somepassword"
        })
        last_user = User.objects.last()
        self.assertNotEqual(last_user.username, "us", "When passed an invalid username in POST it did saved the user in the DB") # check that user data is not being saved in the DB if POST request contains validation errors
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/register", "Method redirected to wrong URL") # check the method redirect to right URL

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")    # checks that page is rendering
        self.assertTemplateUsed(response, 'login.html', "Method render the wrong template")

    def test_log_user_view(self):
        # creates user instance with hashed password for testing login method
        pw_hash = bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode()
        user = User.objects.create(username="test-user", password=pw_hash)

        # succesful post request
        response = self.client.post(self.log_user_url, {
            "username": "test-user",
            "password": "password"
        })
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/jobs", "Method redirected to wrong URL")

        # test invalid post request
        response = self.client.post(self.log_user_url, {
            "username": "test-another-user",
            "password": "other-password"
        })
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method redirected to wrong URL")

    def test_jobs_view(self):
        # test that if user is not logged id view will redirect to login page
        response = self.client.get(self.jobs_url)
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method did not redirect to login page when user is not logged in")

        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.get(self.jobs_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code") # test that method returns an OK server response(page renders!)
        self.assertTemplateUsed(response, 'jobs.html', "Method render the wrong template")  # test that method renders the right template

        # check that method is redirecting to '/search_job' url if there is a search param in session
        session['what'] = "Software Dev"
        session['where'] = "Dallas"
        session.save()

        response = self.client.get(self.jobs_url)

        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/search_job", "Method redirected to wrong URL")

    def test_search_job_view(self):
        # test user permission
        response = self.client.get(self.search_job_url)
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method did not redirect to login page when user is not logged in")

        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.get(self.search_job_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'jobs.html', "Method render the wrong template")

    def test_tracker_app_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        response = self.client.get(self.tracker_app_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'tracker_app.html', "Method render the wrong template")

    def test_set_job_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        response = self.client.post(self.set_job_url, {
            "title": "Software Tester",
            "company": "Some Company",
            "location": "Dallas, TX",
            "url": "https://www.youtube.com/watch?v=hA_VxnxCHbo&list=PLbpAWbHbi5rMF2j5n6imm0enrSD9eQUaM&index=3"
        })
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code") # redirect() returns a 302 code instead of a 200
        job = Jobs.objects.last()
        self.assertEquals(job.location, "Dallas, TX") # checks that the object posted is being saved

    def test_go_to_job_view(self):
        # test user permission
        response = self.client.get(self.go_to_job_url)
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method did not redirect to login page when user is not logged in")

        session = self.client.session
        session['url'] = "https://www.youtube.com/watch?v=hA_VxnxCHbo&list=PLbpAWbHbi5rMF2j5n6imm0enrSD9eQUaM&index=3"
        session['userid'] = 1
        session.save()

        response = self.client.get(self.go_to_job_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'go_to_job.html', "Method render the wrong template")

    def test_viewed_jobs_handler_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        # check that view redirect to another URL
        response = self.client.get(self.viewed_jobs_handler_url)
        self.assertEquals(response.status_code, 302, "Method did not redirect, it's supposed to return a 302 code")

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
        # test user permission
        response = self.client.get(self.edit_job_url)
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method did not redirect to login page when user is not logged in")

        session = self.client.session
        session['userid'] = 1
        session.save()

        response = self.client.get(self.edit_job_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'edit_job.html', "Method render the wrong template")

        # check that job passed(as an id) is the one returned in context
        self.assertEquals(response.context["job"], self.job)

    # check that all job attributes were updated
    def test_update_job_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        response = self.client.post(self.update_job_url, {
            "status": "Interviewing",
            "title": "New job title",
            "company": "New company name",
            "location": "Middle of nowhere"
        })
        self.assertEquals(response.status_code, 302, "Method did not redirect, it's supposed to return a 302 code")   # checks that the method redirects succesfully

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
        session['userid'] = self.user.id
        session.save()

        # validate the method used to check that user has the authorization to delete the job
        self.assertTrue(self.job.user_jobs == self.user, "Logged user is not the one that created the job instance")

        response = self.client.delete(self.delete_job_url)
        self.assertEquals(response.status_code, 302, "Method did not redirect, it's supposed to return a 302 code")   # checks that the method redirects succesfully

        # make sure that the job was deleted
        job = Jobs.objects.last()
        self.assertIsNone(job, "Job was not deleted")

    def test_job_note_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        # validate the method used to check that user has the authorization to view the job note
        self.assertTrue(self.job.user_jobs == self.user, "Logged user is not the one that created the job instance")

        response = self.client.get(self.job_note_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'note.html', "Method render the wrong template")

        # check that the job in context is the same job selected by the user
        self.assertTrue(response.context["job"] == self.job, "Job passed as parameter is not the same one in context")

        # check that the note in context is the same note of the job instance passed
        self.assertTrue(response.context["note"] == self.job.note, "Note in context is not the same one from the job passed")

    # make sure that redirect return 302(which means redirect was a success), job note is updated & validate the user authorization
    def test_update_note_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        # validate the method used to check that user has the authorization to edit the job note
        self.assertTrue(self.job.user_jobs == self.user, "Logged user is not the one that created the job instance")

        response = self.client.post(self.update_note_url, {
            "note": "Some text here about the application that we want to save in notes"
        })
        self.assertEquals(response.status_code, 302, "Method did not redirect, it's supposed to return a 302 code")   # checks that the method redirects succesfully

        job = Jobs.objects.last()
        self.assertEquals(job.note, "Some text here about the application that we want to save in notes", "Job note was not updated")

    def test_new_job_view(self):
        session = self.client.session
        session['userid'] = self.user.id
        session.save()

        response = self.client.get(self.new_job_url)
        self.assertEquals(response.status_code, 200, "Page is not rendering. It's supposed to return a 200 code")
        self.assertTemplateUsed(response, 'new_job.html', "Method render the wrong template")

        # check that the user in context is the correct user
        self.assertTrue(response.context['user_id'] == self.user.id, f"The id ({self.user.id}) of the User that render the form is not the same as the one in context({response.context['user_id']})")

    def test_add_job_view(self):
        # test user permission
        response = self.client.post(self.add_job_url)
        self.assertEquals(response.status_code, 302, "Page did not redirect, it's supposed to return a 302 code")
        self.assertEquals(response.url, "/", "Method did not redirect to login page when user is not logged in")

        session = self.client.session
        session['userid'] = 1
        session.save()

        # test that all attributes are being added correctly to the new job instance
        response = self.client.post(self.add_job_url, {
            "user_jobs": self.user.id,
            "status": "Applied",
            "title": "Amazon CEO",
            "company": "Amazon Inc.",
            "url": "https://somewhere.com/",
            "location": "Seattle, WA"
        })
        self.assertEquals(response.status_code, 302, "Method did not redirect, it's supposed to return a 302 code")
        new_job = Jobs.objects.last()
        self.assertEquals(new_job.user_jobs, self.user, "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.status, "Applied", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.title, "Amazon CEO", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.url, "https://somewhere.com/", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.location, "Seattle, WA", "Method did not use the attribute passed in POST")

        # test that when passed empty attributes the job instance will add None value to those attributes
        response = self.client.post(self.add_job_url, {
            "user_jobs": self.user.id,
            "status": "Applied",
            "title": "",
            "company": "",
            "url": "",
            "location": "   "
        })
        new_job = Jobs.objects.last()
        self.assertEquals(new_job.user_jobs, self.user, "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.status, "Applied", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.title, "None Provided", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.url, "None Provided", "Method did not use the attribute passed in POST")
        self.assertEquals(new_job.location, "None Provided", "Method did not use the attribute passed in POST")
