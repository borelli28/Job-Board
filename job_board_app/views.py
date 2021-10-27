from django.shortcuts import render, redirect
from job_board_app.models import *
from django.contrib import messages
import bcrypt
import requests
import sys
import dotenv
import os
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

def register(request):

    return render(request, 'register.html')

def register_user(request):

    errors = User.objects.user_register_val(request.POST)
    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        # if the errors dictionary contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/register')

    else:
        _username = request.POST['username']
        _password = request.POST['password']

        pw_hash = bcrypt.hashpw(_password.encode(), bcrypt.gensalt()).decode()

        user = User.objects.create(username=_username, password=pw_hash)

        print("User Created:")
        print(User.objects.last().username)

        request.session['userid'] = user.id

        return redirect('/jobs')

# renders the login page
def login(request):

    return render(request, 'login.html')

def logout(request):
    request.session.clear()
    return redirect('/')

# handles the data from user login in login.html
def log_user(request):

    errors = User.objects.user_login_validator(request.POST)
    # check if the errors dictionary has anything in it
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        # redirect the user back to the form to fix the errors
        return redirect('/')

    else:
        # see if the username provided exists in the database.
        user = User.objects.filter(username=request.POST['username'])

        if len(user) > 0:
            logged_user = user[0]

            if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
                request.session['userid'] = logged_user.id
                request.session['username'] = request.POST['username']

                return redirect('/jobs')

    # if we didn't find anything in the database by searching by username or if the passwords don't match,
    return redirect('/')

# render jobs page
def jobs(request):

    if 'userid' in request.session:

        # if what and where are not empty then execute search_job method with this values
        if ('what' in request.session) or ('where' in request.session):
            return redirect('/search_job')
        else:
            return render(request, 'jobs.html')
    else:
        return redirect('/')

# makes API call for jobs and then re render the page with the response from the API
def search_job(request):

    if 'userid' in request.session:

        what = ""
        where = ""

        # if the user goes back to job results page then we use the parameters in session to return job results
        if 'what' in request.session:
            what = request.session['what']
            where = request.session['where']

        if 'what' in request.POST:
            what = request.POST['what']
            request.session['what'] = what
        else:
            print("['what'] empty")

        if 'where' in request.POST:
            where = request.POST['where']
            request.session['where'] = where
        else:
            print("['where'] empty")

        print("what:" + what)
        print("where: " + where)

        dotenv.read_dotenv()
        the_id = os.environ.get('api_app_id')
        the_key = os.environ.get('api_key')

        parameters = {
            "Host": "data.usajobs.gov",
            "User-Agent": "N/A",
            "Authorization-Key": the_key
        }

        # response = requests.get(f"http://api.adzuna.com:80/v1/api/jobs/us/search/1?app_id={the_id}&app_key={the_key}&results_per_page=100&what={what}&where={where}&content-type=application/json")
        response = requests.get(url="https://data.usajobs.gov/api/Search?Keyword=engineer&ResultsPerPage=1", headers=parameters)
        # print("API response:")
        # print(response.json())
        data = response.json()
        results = data["SearchResult"]["SearchResultItems"]
        print("results:")
        print(results)

        # get each job data in an array of objects
        jobs = []
        for job in results:
            print("job:")
            print(" ")
            print(job)
            print("___END OF JOB____")
            temp_obj = {}
            temp_obj["title"] = job["MatchedObjectDescriptor"]["PositionTitle"]
            temp_obj["company"] = job["MatchedObjectDescriptor"]["OrganizationName"]
            temp_obj["location"] = job["MatchedObjectDescriptor"]["PositionLocationDisplay"]
            temp_obj["url"] = job["MatchedObjectDescriptor"]["ApplyURI"]
            temp_obj["description"] = job["MatchedObjectDescriptor"]["QualificationSummary"]
            jobs.append(temp_obj)

        # paginator code: https://www.youtube.com/watch?v=5FKL_voZuFw
        p = Paginator(jobs, 9)
        print("p:")
        print(p)
        page_num = request.GET.get("page", 1)
        print("page_num: ")
        print(page_num)
        # this try block make sure if the user access a page that has not results then he will be redirect to page 1 instead of a server error
        try:
            page = p.page(page_num)
            print("page: ")
            print(page)
        except EmptyPage:
            page = p.page(1)

        # send alert if num of pages is 0
        num_pages = len(page)

        return render(request, 'jobs.html', { "jobs": page, "page_range": p.page_range, "num_pages": num_pages})

    else:
        return redirect('/')

# renders the tracker app page
def tracker_app(request):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])
        print("username:")
        print(user.username)
        print("id:")
        print(request.session['userid'])

        # get jobs viewed
        jobs = Jobs.objects.filter(user_jobs=user)
        print("user jobs:")
        print(len(jobs))

        viewed_jobs = []

        for job in jobs:
            if job.status == "Viewed":
                # append to viewed jobs
                viewed_jobs.append(job)

        # Only show jobs in the table that user apply to.
        jobs = Jobs.objects.filter(user_jobs=user).exclude(status="Viewed")

        # paginator code: https://www.youtube.com/watch?v=5FKL_voZuFw
        p = Paginator(viewed_jobs, 3)
        page_num = request.GET.get("page", 1)
        # this try block make sure if the user access a page that has not results then he will be redirect to page 1 instead of a server error
        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)

        # table paginator
        table_p = Paginator(jobs, 20)
        table_page_num = request.GET.get("page", 1)
        # this try block make sure if the user access a page that has not results then he will be redirect to page 1 instead of a server error
        try:
            table_page = table_p.page(table_page_num)
        except EmptyPage:
            table_page = table_p.page(1)

        context = {"user_jobs":table_page, "viewed_jobs": page}

        return render(request, 'tracker_app.html', context)

    else:
        return redirect('/')

# get the job details of the job clicked and saved them in the DB
def set_job(request):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        # get job info
        _title = request.POST['title']
        _company = request.POST['company']
        _location = request.POST['location']
        _url = request.POST['url']

        request.session['url'] = _url

        print("title: " + _title + " company: " + _company + " location: " + _location + " url: " + _url)


        # create job instance
        job= Jobs.objects.create(title=_title, company=_company, url=_url, location=_location, user_jobs=user)

        print("job instance created:")
        print(job.title)

        return redirect('/go_to_job')

    else:
        return redirect('/')

def go_to_job(request):

    if 'userid' in request.session:

        url = request.session['url']

        context = {"url": url}

        return render(request, 'go_to_job.html', context)

    else:
        return redirect('/')

# handles viewed jobs form data(add to applied or delete)
def viewed_jobs_handler(request, id):

    if 'userid' in request.session:

        # get job instance
        job = Jobs.objects.get(id=id)

        try:
            # user applied to the job so change job status to applied
            if 'yes' in request.POST["applied?"]:
                job.status = "Applied"
                job.title = strip_tags(job.title)
                job.save()
                print("user clicked yes so status was updated:")
                print(job.status)

            # user did not applied to the job so delete it
            if 'no' in request.POST["applied?"]:
                job.delete()
                print("job deleted")
        except:
            print("Error ocurred while getting the post response. Probably user submit empty form")
            return redirect('/tracker_app')

        return redirect('/tracker_app')

    else:
        return redirect('/')

# renders edit job form
def edit_job(request, id):

    if 'userid' in request.session:

        # get job instance
        job = Jobs.objects.get(id=id)

        context = {"job": job}

        return render(request, 'edit_job.html', context)

    else:
        return redirect('/')

# handles job put data from form
def update_job(request, id):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        # get job instance
        job = Jobs.objects.get(id=id)

        # NOTE: if the if statement argument is changed you need to update the test case in: tests/test_views.py - line: 141
        # check that the job we are editing belongs to the logged user
        if job.user_jobs == user:

            _status = request.POST['status']
            _title = request.POST['title']
            _company = request.POST['company']

            # TODO: Add way to update location in the form(front end) and the logic here too

            job.status = _status
            job.title = _title
            job.company = _company
            job.save()

            print("Job was updated")
            return redirect('/tracker_app')

        else:
            print("User don't have permission to edit this Job object")
            return redirect('/tracker_app')

    else:
        return redirect('/')

def delete_job(request, id):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        # get job instance
        job = Jobs.objects.get(id=id)

        # NOTE: if the if statement argument is edited makes sure to edit the test case for this method too. Line: 153 in test_views.py
        # check that the job we are deleting belongs to the logged user
        if job.user_jobs == user:
            job.delete()
            print("job deleted")
            return redirect('/tracker_app')
        else:
            print("User don't have permission to delete this Job object")
            return redirect('/tracker_app')

    else:
        return redirect('/')

# renders note page
def job_note(request, id):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        # get job instance
        job = Jobs.objects.get(id=id)

        # NOTE: if the if statement argument is edited makes sure to edit the test case for this method too. Line: 169 in test_views.py
        # check that logged user is the owner of this job instance
        if job.user_jobs == user:
            note = job.note
            context = { "note": note, "job": job }
            return render(request, 'note.html', context)

        else:
            print("User don't have permission to access these resources")
            return redirect('/tracker_app')

    else:
        return redirect('/')

# update job note
def update_note(request, id):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        # get job instance
        job = Jobs.objects.get(id=id)

        # check that logged user is the owner of this job instance
        if job.user_jobs == user:
            note = request.POST['note']
            job.note = note
            job.save()
            print("Note updated")
            return redirect('/tracker_app')

        else:
            print("User don't have permission to access these resources")
            return redirect('/tracker_app')

    else:
        return redirect('/')

# renders the add job manually form
def new_job(request):

    if 'userid' in request.session:

        user = User.objects.get(id=request.session['userid'])

        context = {"user_id": user.id}
        return render(request, 'new_job.html', context)

    else:
        return redirect('/')

# handles the post form data from new_job template
def add_job(request):

    if 'userid' in request.session:

        if 'user_jobs' in request.POST:
            user_id = request.POST['user_jobs']
            _user = User.objects.get(id=user_id)

            if 'status' in request.POST:
                _status = request.POST['status']
            else:
                _status = "Applied"

            if request.POST['title'] and not request.POST['title'].isspace():
                _title = request.POST['title']
            else:
                _title = "None Provided"

            if request.POST['company'] and not request.POST['company'].isspace():
                _company = request.POST['company']
            else:
                _company = "None Provided"

            if request.POST['url'] and not request.POST['url'].isspace():
                _url = request.POST['url']
            else:
                _url = "None Provided"

            if request.POST['location'] and not request.POST['location'].isspace():
                _location = request.POST['location']
            else:
                _location = "None Provided"

            new_job = Jobs.objects.create(status=_status, title=_title, company=_company, url=_url, location=_location, user_jobs=_user)
            print("new job created: " + str(new_job.title))

            return redirect('/tracker_app')

        else:
            return redirect('/tracker_app/new_job_form')

    else:
        return redirect('/')

def delete_all_viewed_jobs(request):
    pass
