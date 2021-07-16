from django.test import SimpleTestCase
from django.urls import reverse, resolve
from job_board_app.views import *

#   ./manage.py test job_board_app                  *activate virtualenv to run tests*

class TestUrls(SimpleTestCase):

    # test url by: checking the url name resolves to the views method
    def test_index_url(self):
        url = reverse("index")
        self.assertEquals(resolve(url).func, index)

    def test_render_jobs_url(self):
        url = reverse("render_jobs")
        self.assertEquals(resolve(url).func, jobs)

    def test_job_search_logic_url(self):
        url = reverse("job_search_logic")
        self.assertEquals(resolve(url).func, search_job)

    def test_render_tracker_app_url(self):
        url = reverse("render_tracker_app")
        self.assertEquals(resolve(url).func, tracker_app)

    def test_save_job_info_url(self):
        url = reverse("save_job_info")
        self.assertEquals(resolve(url).func, set_job)

    def test_go_to_job_url(self):
        url = reverse("go_to_job")
        self.assertEquals(resolve(url).func, go_to_job)

    def test_viewed_job_handler_url(self):
        url = reverse("viewed_job_handler", args=["1"])
        self.assertEquals(resolve(url).func, viewed_jobs_handler)
