from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('jobs', views.jobs),
    path('search_job', views.search_job),
    path('tracker-app', views.tracker_app)
]
