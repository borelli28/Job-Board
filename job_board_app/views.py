from django.shortcuts import render, HttpResponse, redirect
from job_board_app.models import *
import requests
import sys
import dotenv
import os


def index(request):

    # get user id and save it into session
    user = User.objects.get(id=1)

    request.session['userid'] = 1

    return HttpResponse("hello")

# render jobs page
def jobs(request):
    return render(request, 'jobs.html')

# makes API call to indeed.com for jobs and then re render the page with the response from the API
def search_job(request):
    print("inside search_job")

    what = ""
    where = ""

    if "what" in request.POST:
        what = request.POST["what"]
    else:
        print("['what'] empty")

    if "where" in request.POST:
        where = request.POST["where"]
    else:
        print("['where'] empty")

    print("what:" + what)
    print("where: " + where)

    dotenv.read_dotenv()
    the_id = os.environ.get('api_app_id')
    the_key = os.environ.get('api_key')

    # response = requests.get("http://lookup-service-prod.mlb.com/json/named.search_player_all.bam/json/named.sport_hitting_tm.bam?league_list_id='mlb'&game_type='R'&season='2021'&player_id='545361'")
    # response = requests.get(f"http://api.adzuna.com/v1/api/jobs/us/search/1?app_id={the_id}&app_key={the_key}&results_per_page=1&what=javascript%20developer&content-type=application/json")
    # response = requests.get(f"http://api.adzuna.com:80/v1/api/jobs/us/search/1?app_id={the_id}&app_key={the_key}&results_per_page=5&what=javascript%20developer&what_exclude=java&where=nc&content-type=application/json")

    response = requests.get(f"http://api.adzuna.com:80/v1/api/jobs/us/search/1?app_id={the_id}&app_key={the_key}&results_per_page=5&what={what}&where={where}&content-type=application/json")

    # print("response:")
    # print(response.text)
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


    return render(request, 'jobs.html', { "jobs": jobs })

# renders the tracker app page
def tracker_app(request):

    return render(request, 'tracker_app.html')

# get the job details of the job clicked and saved them in the DB
def set_job(request):

    # get user instance
    user = User.objects.get(id=request.session['userid'])

        # status = models.CharField(max_length=20)
        # title = models.CharField(max_length=50)
        # company = models.CharField(max_length=50)
        # url = models.CharField(max_length=255)
        # location = models.CharField(max_length=255)
        # date_submitted = models.DateField(default=date.today)
        # user_jobs = models.ForeignKey(User, related_name="user", on_delete=models.CASCADE)

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

    # return redirect(f'{_url}')
    return redirect('/go_to_job')

def go_to_job(request):

    url = request.session['url']

    context = {"url": url}

    return render(request, 'go_to_job.html', context)
