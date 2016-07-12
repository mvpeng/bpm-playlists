from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from urllib import urlencode
import random, math, os, base64
import requests
from . import utils, settings

STATE_KEY = 'spotify_auth_state'

def index(request):
    return render(request, 'index.html')

def create(request):
    request.session['playlist_info'] = request.POST
    return login(request)

def login(request):
    scope = 'playlist-modify-public playlist-modify-private user-library-read'
    state = utils.generateRandomString(16)
    query = urlencode({ 'response_type': 'code',
                        'client_id': settings.CLIENT_ID,
                        'scope': scope,
                        'redirect_uri': settings.REDIRECT_URI,
                        'state': state })
    
    response = HttpResponseRedirect('https://accounts.spotify.com/authorize?' + query)
    response.set_signed_cookie(STATE_KEY, state)
    return response

def callback(request):
    authorization_code = request.GET['code']
    state = request.GET['state']
    storedState = request.get_signed_cookie(STATE_KEY, False)
    access_token = None

    if state == None or state != storedState:
        return render(request, 'index.html', {'error_message': "Could not authenticate. State mismatch."})
    else:
        # exchange authorization_code for an access_token
        url = 'https://accounts.spotify.com/api/token'
        headers = {'Authorization': 'Basic ' + base64.b64encode(settings.CLIENT_ID + ':' + settings.CLIENT_SECRET)}
        body = {'code': authorization_code, 
                'redirect_uri': settings.REDIRECT_URI, 
                'grant_type': 'authorization_code'}

        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            body = response.json()
            access_token = body['access_token']
            refresh_token = body['refresh_token']
        else:
            return render(request, 'index.html', {'error_message': "Could not get token."})

        playlist_songs = utils.createPlaylistWithBPM(request.session['playlist_info'], access_token)
        context = { 'playlist_info': request.session['playlist_info'], 
                    'playlist_songs': playlist_songs }
        return render(request, 'index.html', context)