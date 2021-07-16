from django.test import TestCase
from django.urls import reverse, resolve
from job_board_app.views import *

# Create your tests here.
class TestUrls(TestCase):

    def test_render_tracker_app_url(self):
        url = reverse("index")
        print(resolve(url))
        self.assertEquals(resolve(url).func, tracker_app)
