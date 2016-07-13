import requests
import math, random
import json

def createPlaylistWithBPM(playlist_info, access_token):
    tracks = getUsersMostRecentTracks(access_token)
    tracks = filterTracksByBPM(tracks, playlist_info['min_bpm'], playlist_info['max_bpm'], access_token)
    playlistURI =  createAndPopulatePlaylist(playlist_info['playlist_name'], tracks, access_token)
    return {'uri': playlistURI, 'tracks': tracks}

def getUsersMostRecentTracks(access_token):
    url = 'https://api.spotify.com/v1/me/tracks'
    headers = {'Authorization': 'Bearer ' + access_token}
    params = {'limit': 50, 'offset': 0 }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['items']

def filterTracksByBPM(tracks, minBPM, maxBPM, access_token):
    url = 'https://api.spotify.com/v1/audio-features'
    headers = {'Authorization': 'Bearer ' + access_token}

    ids = ""
    for track in tracks:
        ids += str(track['track']['id']) + ","
    response = requests.get(url, headers=headers, params={'ids': ids})
    
    filtered = []
    if response.status_code == 200:
        results = response.json()['audio_features']
        for i in xrange(len(tracks)):
            tracks[i]['track']['bpm'] = results[i]['tempo']
        
        if minBPM != "" and maxBPM != "":
            for track in tracks:
                bpm = track['track']['bpm']
                if bpm >= int(minBPM) and bpm <= int(maxBPM):
                    filtered.append(track)
        else:
            filtered = tracks
    return filtered

def createAndPopulatePlaylist(playlistName, tracks, access_token):
    userId = getUserId(access_token)
    playlist = createPlaylist(userId, playlistName, access_token)
    addTracksToPlaylist(userId, playlist['id'], tracks, access_token)
    return playlist['uri']

def getUserId(access_token):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    if response.status_code == 200:
        return response.json()['id']

def createPlaylist(userId, playlistName, access_token):
    url = 'https://api.spotify.com/v1/users/' + userId + '/playlists'
    headers = { 'Authorization': 'Bearer ' + access_token, 
                'Content-Type': 'application/json' }
    body = json.dumps({ 'name': playlistName , 'public': False })

    response = requests.post(url, headers=headers, data=body)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()

def addTracksToPlaylist(userId, playlistId, tracks, access_token):
    url = 'https://api.spotify.com/v1/users/' + userId + '/playlists/' + playlistId + '/tracks'
    headers = { 'Authorization': 'Bearer ' + access_token, 
                'Content-Type': 'application/json' }
    uris = []
    for track in tracks:
        uris.append(track['track']['uri'])
    body = json.dumps({ 'uris': uris })

    response = requests.post(url, headers=headers, data=body)

def generateRandomString(length):
    result = ''
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for i in xrange(length):
        result += possible[int(math.floor(random.random() * len(possible)))]
    return result