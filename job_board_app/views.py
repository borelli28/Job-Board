from django.shortcuts import render, HttpResponse, redirect
from job_board_app.models import *
import requests
import sys
import dotenv
import os
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage


def index(request):

    # get user id and save it into session
    user = User.objects.get(id=1)

    request.session['userid'] = 1

    return HttpResponse("hello")

# render jobs page
def jobs(request):

    return render(request, 'jobs.html')

# makes API call for jobs and then re render the page with the response from the API
def search_job(request):
    print("inside search_job")

    what = ""
    where = ""

    if 'what' in request.POST:
        what = request.POST["what"]
    else:
        print("['what'] empty")

    if 'where' in request.POST:
        where = request.POST["where"]
    else:
        print("['where'] empty")

    print("what:" + what)
    print("where: " + where)

    dotenv.read_dotenv()
    the_id = os.environ.get('api_app_id')
    the_key = os.environ.get('api_key')

    response = requests.get(f"http://api.adzuna.com:80/v1/api/jobs/us/search/1?app_id={the_id}&app_key={the_key}&what={what}&where={where}&content-type=application/json")

    data = response.json()
    results = data["results"]

    # get each job data
    jobs = []

    for job in results:
        temp_obj = {}
        temp_obj["title"] = job["title"]
        temp_obj["company"] = job["company"]["display_name"]
        temp_obj["location"] = job["location"]["display_name"]
        temp_obj["url"] = job["redirect_url"]
        temp_obj["description"] = job["description"]
        jobs.append(temp_obj)

    # paginator code: https://www.youtube.com/watch?v=5FKL_voZuFw
    p = Paginator(jobs, 6)
    page_num = request.GET.get("page", 1)
    # this try block make sure if the user access a page that has not results then he will be redirect to page 1 instead of a server error
    try:
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    return render(request, 'jobs.html', { "jobs": page })

# renders the tracker app page
def tracker_app(request):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

    # get jobs viewed
    jobs = Jobs.objects.filter(user_jobs=user)

    viewed_jobs = []

    for job in jobs:
        if job.status == "Viewed":
            # append to viewed jobs
            viewed_jobs.append(job)

    # Only show jobs in the table that user apply to.
    jobs = Jobs.objects.exclude(status="Viewed")

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

# get the job details of the job clicked and saved them in the DB
def set_job(request):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

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

def go_to_job(request):

    url = request.session['url']

    context = {"url": url}

    return render(request, 'go_to_job.html', context)

# handles viewed jobs form data(add to applied or delete)
def viewed_jobs_handler(request, id):

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

# renders edit job form
def edit_job(request, id):

    # get job instance
    job = Jobs.objects.get(id=id)

    context = {"job": job}

    return render(request, 'edit_job.html', context)

# handles job put data from form
def update_job(request, id):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

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

def delete_job(request, id):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

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

# renders note page
def job_note(request, id):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

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

# update job note
def update_note(request, id):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')
    user = User.objects.get(id=user_id)

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

# renders the add job manually form
def new_job(request):
    # get logged user
    dotenv.read_dotenv()
    user_id = os.environ.get('user_id')

    context = {"user_id": user_id}
    return render(request, 'new_job.html', context)

# handles the post form data from new_job template
def add_job(request):

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
