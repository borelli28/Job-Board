from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name="register"),
    path('register_user', views.register_user, name="register_user"),
    path('', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('log_user', views.log_user, name="log_user"),
    path('jobs', views.jobs, name="render_jobs"),
    path('search_job', views.search_job, name="job_search_logic"),
    path('tracker_app', views.tracker_app, name="render_tracker_app"),
    path('set_job', views.set_job, name="save_job_info"),
    path('go_to_job', views.go_to_job, name="go_to_job"),
    path('tracker_app/handle_viewed_job/<int:id>', views.viewed_jobs_handler, name="viewed_job_handler"),
    path('tracker_app/edit_job/<int:id>', views.edit_job, name="edit_job_form"),
    path('tracker_app/edit_job/update/<int:id>', views.update_job, name="update_job_logic"),
    path('tracker_app/edit_job/delete/<int:id>', views.delete_job, name="delete_job"),
    path('tracker_app/notes/<int:id>', views.job_note, name="render_job_note"),
    path('tracker_app/notes/update/<int:id>', views.update_note, name="update_job_note"),
    path('tracker_app/new_job_form', views.new_job, name="new_job_form"),
    path('tracker_app/add_new_job', views.add_job, name="add_job"),
    path('tracker_app/delete_all_viewed_jobs', views.delete_all_viewed_jobs, name="delete_all_viewed_jobs")
]
