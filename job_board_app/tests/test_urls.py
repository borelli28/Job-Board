from django.test import SimpleTestCase
from django.urls import reverse, resolve
from job_board_app.views import *

#   ./manage.py test job_board_app                  *activate virtualenv to run tests*

class TestUrls(SimpleTestCase):

    # test url by: checking the url name resolves to the views method
    def test_register_url(self):
        url = reverse("register")
        self.assertEquals(resolve(url).func, register, "register url does not link to the method [register] in views")

    def test_register_user_url(self):
        url = reverse("register_user")
        self.assertEquals(resolve(url).func, register_user, "register_user url does not link to the method [register_user] in views")

    def test_login_url(self):
        url = reverse("login")
        self.assertEquals(resolve(url).func, login, "login url does not link to the method [login] in views")

    def test_log_user_url(self):
        url = reverse("log_user")
        self.assertEquals(resolve(url).func, log_user, "log_user url does not link to the method [log_user] in views")

    def test_render_jobs_url(self):
        url = reverse("render_jobs")
        self.assertEquals(resolve(url).func, jobs, "render_jobs url does not link to the method [jobs] in views")

    def test_job_search_logic_url(self):
        url = reverse("job_search_logic")
        self.assertEquals(resolve(url).func, search_job, "job_search_logic url does not link to the method [search_job] in views")

    def test_render_tracker_app_url(self):
        url = reverse("render_tracker_app")
        self.assertEquals(resolve(url).func, tracker_app, "render_tracker_app url does not link to the method [tracker_app] in views")

    def test_save_job_info_url(self):
        url = reverse("save_job_info")
        self.assertEquals(resolve(url).func, set_job, "save_job_info url does not link to the method [set_job] in views")

    def test_go_to_job_url(self):
        url = reverse("go_to_job")
        self.assertEquals(resolve(url).func, go_to_job, "go_to_job url does not link to the method [go_to_job] in views")

    def test_viewed_job_handler_url(self):
        url = reverse("viewed_job_handler", args=["1"])
        self.assertEquals(resolve(url).func, viewed_jobs_handler, "viewed_job_handler url does not link to the method [viewed_job_handler] in views")

    def test_edit_job_form_url(self):
        url = reverse("edit_job_form", args=["1"])
        self.assertEquals(resolve(url).func, edit_job, "edit_job_form url does not link to the method [edit_job] in views")

    def test_update_job_logic_url(self):
        url = reverse("update_job_logic", args=["1"])
        self.assertEquals(resolve(url).func, update_job, "update_job_logic url does not link to the method [update_job] in views")

    def test_delete_job_url(self):
        url = reverse("delete_job", args=["1"])
        self.assertEquals(resolve(url).func, delete_job, "delete_job url does not link to the method [delete_job] in views")

    def test_render_job_note_url(self):
        url = reverse("render_job_note", args=["1"])
        self.assertEquals(resolve(url).func, job_note, "render_job_note url does not link to the method [job_note] in views")

    def test_update_job_note_url(self):
        url = reverse("update_job_note", args=["1"])
        self.assertEquals(resolve(url).func, update_note, "update_job_note url does not link to the method [update_note] in views")

    def test_new_job_url(self):
        url = reverse("new_job_form")
        self.assertEquals(resolve(url).func, new_job, "new_job_form url does not link to the method [new_job] in views")

    def test_add_job_url(self):
        url = reverse("add_job")
        self.assertEquals(resolve(url).func, add_job, "add_job_form url does not link to the method [add_job] in views")
