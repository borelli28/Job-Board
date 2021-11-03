from django.db import models
from datetime import date, datetime

class ValidatorManager(models.Manager):

    def user_register_val(self, postData):
        errors = {}

        if len(postData['username']) < 3:
            errors["username"] = "Username should be at least 3 characters long"

        if len(postData['username']) >= 30:
            errors["username"] = "Username cannot be longer than 30 characters"

        if len(postData['password']) < 8:
            errors["password"] = "Password should be at least 8 characters"

        if postData['password'] != postData['confirm_password']:
            errors["password"] = "Passwords do not match"

        if User.objects.filter(username=postData['username']):
            errors["username"] = "Username is not valid. Please enter a valid username"

        return errors

    def user_login_validator(self, postData):
        errors = {}

        if len(postData['password']) < 8:
            errors["password"] = "Password should be at least 8 characters"

        if len(postData['username']) < 3:
            errors["username"] = "Username should be at least 3 characters long"

        if User.objects.filter(username=postData['username']):
            pass
        else:
            errors['username'] = "You enter the wrong username or password. Try again"

        return errors

class User(models.Model):

    username = models.CharField(max_length=30)
    # email = models.EmailField(max_length=254)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ValidatorManager()

class Jobs(models.Model):

    status = models.CharField(max_length=20, default="Viewed")
    title = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    date_submitted = models.DateField(default=date.today)
    user_jobs = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)
    note = models.TextField(default="Enter text here")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
