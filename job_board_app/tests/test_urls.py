from django.test import SimpleTestCase
from django.urls import reverse, resolve
from job_board_app.views import *

class TestUrls(SimpleTestCase):

    def test_index_url(self):
        url = reverse("index")
        print(resolve(url))
        self.assertEquals(resolve(url).func, index)
