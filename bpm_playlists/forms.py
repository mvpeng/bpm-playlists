from django import forms

class BPMPlaylistForm(forms.Form):
    min_bpm = forms.IntegerField(label='Min', max_value=500, min_value=0)
    max_bpm = forms.IntegerField(label='Max', max_value=500, min_value=0)
    playlist_name = forms.CharField(label='Playlist name', max_length=50)