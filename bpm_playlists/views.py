from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from urllib import urlencode
import random, math, os, base64
import requests

CLIENT_ID= '4df0271d6b1f4768a5bd929a13091e8b'
CLIENT_SECRET = os.environ.get('BPMPLAYLISTS_SECRET_KEY')
REDIRECT_URI = 'http://localhost:8000/callback'

STATE_KEY = 'spotify_auth_state'

def index(request):
    return render(request, 'index.html')

def login(request):
    scope = 'user-read-private user-read-email'
    state = generateRandomString(16)
    query = urlencode({ 'response_type': 'code',
                        'client_id': CLIENT_ID,
                        'scope': scope,
                        'redirect_uri': REDIRECT_URI,
                        'state': state })
    
    response = HttpResponseRedirect('https://accounts.spotify.com/authorize?' + query)
    response.set_signed_cookie(STATE_KEY, state)
    return response

def callback(request):
    authorization_code = request.GET.get('code')
    state = request.GET.get('state')
    storedState = request.get_signed_cookie(STATE_KEY, False)

    if state == None or state != storedState:
        return HttpResponse("Could not authenticate. State mismatch.")
    else:
        # exchange authorization_code for an access_token
        url = 'https://accounts.spotify.com/api/token'
        headers = {'Authorization': 'Basic ' + base64.b64encode(CLIENT_ID + ':' + CLIENT_SECRET)}
        body = {'code': authorization_code, 
                'redirect_uri': REDIRECT_URI, 
                'grant_type': 'authorization_code'}

        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            body = response.json()
            access_token = body['access_token']
            refresh_token = body['refresh_token']
        else:
            return HttpResponse("Could not get token.")

        return render(request, 'callback.html')


def generateRandomString(length):
    result = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for i in xrange(length):
        result += possible[int(math.floor(random.random() * len(possible)))]
    return result