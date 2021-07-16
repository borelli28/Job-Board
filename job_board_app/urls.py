from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('jobs', views.jobs),
    path('search_job', views.search_job, name="index"),
    path('tracker_app', views.tracker_app, name="index"),
    path('set_job', views.set_job),
    path('go_to_job', views.go_to_job),
    path('tracker_app/handle_viewed_job/<int:id>', views.viewed_jobs_handler),
    path('tracker_app/edit_job/<int:id>', views.edit_job),
    path('tracker_app/edit_job/update/<int:id>', views.update_job),
    path('tracker_app/edit_job/delete/<int:id>', views.delete_job)
]
