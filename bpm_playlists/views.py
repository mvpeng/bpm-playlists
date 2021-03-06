from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from urllib import urlencode
import random, math, os, base64
import requests
from . import utils
from .forms import BPMPlaylistForm

# Spotify API keys
CLIENT_ID= '4df0271d6b1f4768a5bd929a13091e8b'
CLIENT_SECRET = os.environ.get('BPMPLAYLISTS_CLIENT_SECRET')

REDIRECT_URI = '/callback'
STATE_KEY = 'spotify_auth_state'

def index(request):
    preview_tracks = utils.getPreviewTracks()
    return render(request, 'index.html', {'preview_tracks': preview_tracks})

def create(request):
    form = BPMPlaylistForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        if data['min_bpm'] > data ['max_bpm']:
            return render(request, 'index.html', {'error_message': "Min BPM must be smaller than or equal to Max BPM"})
        request.session['playlist_info'] = data
        return login(request)
    return render(request, 'index.html', {'error_message': "Please set BPM and name values."})

def login(request):
    scope = 'playlist-modify-public playlist-modify-private user-library-read'
    state = utils.generateRandomString(16)
    query = urlencode({ 'response_type': 'code',
                        'client_id': CLIENT_ID,
                        'scope': scope,
                        'redirect_uri': request.build_absolute_uri(REDIRECT_URI),
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
        headers = {'Authorization': 'Basic ' + base64.b64encode(CLIENT_ID + ':' + CLIENT_SECRET)}
        body = {'code': authorization_code, 
                'redirect_uri': request.build_absolute_uri(REDIRECT_URI), 
                'grant_type': 'authorization_code'}

        response = requests.post(url, headers=headers, data=body)
        if response.status_code == 200:
            body = response.json()
            access_token = body['access_token']
            refresh_token = body['refresh_token']
        else:
            return render(request, 'index.html', {'error_message': "Could not get token."})

        playlist = utils.createPlaylistWithBPM(request.session['playlist_info'], access_token)
        context = { 'playlist_info': request.session['playlist_info'], 
                    'playlist': playlist }
        return render(request, 'index.html', context)