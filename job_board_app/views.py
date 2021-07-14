from django.shortcuts import render, HttpResponse, redirect
import requests
import json

def index(request):
    return redirect('http://localhost:3000/')

def indeed_auth(request):
    print("indeed_auth request:")

    if request.method == 'GET':
        response = requests.get("http://lookup-service-prod.mlb.com/json/named.search_player_all.bam/json/named.sport_hitting_tm.bam?league_list_id='mlb'&game_type='R'&season='2021'&player_id='545361'")
        print(response)
        return HttpResponse(response)
    else:
        print("request method is not GET")

    # return redirect('http://localhost:3000/')
