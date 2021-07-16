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
