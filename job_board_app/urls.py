from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('user/indeed-auth', views.indeed_auth)
]
