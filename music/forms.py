from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Titre, Playlist, Artiste, Album


class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'votre@email.com'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')


class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': "Nom d'utilisateur", 'class': 'form-input'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Mot de passe', 'class': 'form-input'})


class TitreForm(forms.ModelForm):
    class Meta:
        model = Titre
        fields = ['titre', 'artiste', 'album', 'fichier_audio', 'cover',
                  'duree', 'numero_piste', 'genre', 'paroles', 'est_explicite']
        widgets = {
            'titre': forms.TextInput(attrs={'placeholder': 'Titre de la chanson', 'class': 'form-input'}),
            'duree': forms.NumberInput(attrs={'placeholder': 'Durée en secondes', 'class': 'form-input'}),
            'paroles': forms.Textarea(attrs={'rows': 6, 'class': 'form-input'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            try:
                artiste = user.artiste
                self.fields['artiste'].initial = artiste
                self.fields['album'].queryset = Album.objects.filter(artiste=artiste)
            except Exception:
                pass
        for name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-input'


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['nom', 'description', 'cover', 'est_publique']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom de la playlist', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-input', 'placeholder': 'Description...'}),
        }


class ArtisteForm(forms.ModelForm):
    class Meta:
        model = Artiste
        fields = ['nom', 'bio', 'photo', 'genres']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
        }