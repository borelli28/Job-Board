from django.db import models
from datetime import date, datetime

# Create your models here.

class User(models.Model):

    email = models.EmailField(max_length=254)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Jobs(models.Model):

    status = models.CharField(max_length=20, default="viewed")
    title = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_submitted = models.DateField(default=date.today)
    user_jobs = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
