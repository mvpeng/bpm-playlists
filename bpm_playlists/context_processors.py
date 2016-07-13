from . import forms

def bpm_playlist_form_context(request):
    return {'form': forms.BPMPlaylistForm()}