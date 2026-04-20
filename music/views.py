import json
import urllib.parse
import urllib.request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.http import require_POST

from .models import (
    Titre, Album, Artiste, Playlist, Genre,
    FavoriTitre, Historique, ProfilUtilisateur, PlaylistTitre
)
from .forms import InscriptionForm, ConnexionForm, TitreForm, PlaylistForm, ArtisteForm


def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            ProfilUtilisateur.objects.get_or_create(utilisateur=user)
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'auth/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = ConnexionForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'accueil'))
        messages.error(request, "Identifiants incorrects.")
    else:
        form = ConnexionForm()
    return render(request, 'auth/connexion.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    return redirect('connexion')


@login_required
def accueil(request):
    titres_populaires = Titre.objects.order_by('-nb_ecoutes')[:10]
    albums_recents = Album.objects.order_by('-date_sortie')[:8]
    artistes = Artiste.objects.annotate(nb_titres=Count('titres')).order_by('-nb_titres')[:8]
    playlists_user = Playlist.objects.filter(proprietaire=request.user)[:5]
    historique = Historique.objects.filter(utilisateur=request.user).select_related('titre__artiste')[:5]

    artistes_deezer = []
    try:
        url = "https://api.deezer.com/chart/0/artists?limit=20"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            artistes_deezer = data.get('data', [])
    except Exception:
        pass

    context = {
        'titres_populaires': titres_populaires,
        'albums_recents': albums_recents,
        'artistes': artistes,
        'playlists_user': playlists_user,
        'historique': historique,
        'artistes_deezer': artistes_deezer,
    }
    return render(request, 'music/accueil.html', context)


@login_required
def explorer(request):
    genres = Genre.objects.annotate(nb=Count('titre')).order_by('-nb')
    artistes = Artiste.objects.annotate(nb=Count('titres')).order_by('-nb')[:12]
    albums = Album.objects.order_by('-date_sortie')[:12]

    tops_deezer = {}
    genres_deezer = {}
    try:
        categories = {
            'artistes': 'https://api.deezer.com/chart/0/artists?limit=20',
            'titres': 'https://api.deezer.com/chart/0/tracks?limit=20',
            'albums': 'https://api.deezer.com/chart/0/albums?limit=20',
        }
        for key, url in categories.items():
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                tops_deezer[key] = data.get('data', [])

        genres_ids = {
            'Hip-Hop': 116,
            'Afrobeats': 2309,
            'R&B': 15,
            'Pop': 132,
            'Rock': 152,
            'Jazz': 129,
            'Electronique': 106,
            'Reggae': 144,
        }
        for genre_nom, genre_id in genres_ids.items():
            url = f"https://api.deezer.com/chart/{genre_id}/tracks?limit=10"
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read())
                    genres_deezer[genre_nom] = data.get('data', [])
            except Exception:
                genres_deezer[genre_nom] = []

    except Exception:
        pass

    return render(request, 'music/explorer.html', {
        'genres': genres,
        'artistes': artistes,
        'albums': albums,
        'tops_deezer': tops_deezer,
        'genres_deezer': genres_deezer,
    })


@login_required
def recherche(request):
    q = request.GET.get('q', '').strip()
    titres, albums, artistes, playlists = [], [], [], []
    if q:
        titres = Titre.objects.filter(
            Q(titre__icontains=q) | Q(artiste__nom__icontains=q)
        ).select_related('artiste', 'album')[:20]
        albums = Album.objects.filter(
            Q(titre__icontains=q) | Q(artiste__nom__icontains=q)
        ).select_related('artiste')[:10]
        artistes = Artiste.objects.filter(nom__icontains=q)[:8]
        playlists = Playlist.objects.filter(
            Q(nom__icontains=q), est_publique=True
        )[:8]
    return render(request, 'music/recherche.html', {
        'q': q, 'titres': titres, 'albums': albums,
        'artistes': artistes, 'playlists': playlists
    })


@login_required
def detail_titre(request, pk):
    titre = get_object_or_404(Titre, pk=pk)
    est_favori = FavoriTitre.objects.filter(utilisateur=request.user, titre=titre).exists()
    titres_similaires = Titre.objects.filter(genre=titre.genre).exclude(pk=pk)[:5]
    playlists_user = Playlist.objects.filter(proprietaire=request.user)
    return render(request, 'music/titre.html', {
        'titre': titre, 'est_favori': est_favori,
        'titres_similaires': titres_similaires,
        'playlists_user': playlists_user,
    })


@login_required
def ajouter_titre(request):
    if request.method == 'POST':
        form = TitreForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            titre = form.save()
            messages.success(request, f"« {titre.titre} » ajouté avec succès !")
            return redirect('detail_titre', pk=titre.pk)
    else:
        form = TitreForm(user=request.user)
    return render(request, 'music/ajouter_titre.html', {'form': form})


@login_required
@require_POST
def enregistrer_ecoute(request, pk):
    titre = get_object_or_404(Titre, pk=pk)
    Titre.objects.filter(pk=pk).update(nb_ecoutes=titre.nb_ecoutes + 1)
    Historique.objects.create(utilisateur=request.user, titre=titre)
    return JsonResponse({'ok': True, 'nb_ecoutes': titre.nb_ecoutes + 1})


@login_required
@require_POST
def toggle_favori(request, pk):
    titre = get_object_or_404(Titre, pk=pk)
    fav, created = FavoriTitre.objects.get_or_create(utilisateur=request.user, titre=titre)
    if not created:
        fav.delete()
        return JsonResponse({'favori': False})
    return JsonResponse({'favori': True})


@login_required
def mes_favoris(request):
    favoris = FavoriTitre.objects.filter(
        utilisateur=request.user
    ).select_related('titre__artiste', 'titre__album').order_by('-date_ajout')
    return render(request, 'music/favoris.html', {'favoris': favoris})


@login_required
def detail_album(request, slug):
    album = get_object_or_404(Album, slug=slug)
    titres = album.titres.select_related('artiste').order_by('numero_piste')
    return render(request, 'music/album.html', {'album': album, 'titres': titres})


@login_required
def detail_artiste(request, slug):
    artiste = get_object_or_404(Artiste, slug=slug)
    albums = artiste.albums.order_by('-date_sortie')
    titres_populaires = artiste.titres.order_by('-nb_ecoutes')[:5]
    est_abonne = artiste.abonnes.filter(pk=request.user.pk).exists()
    return render(request, 'music/artiste.html', {
        'artiste': artiste, 'albums': albums,
        'titres_populaires': titres_populaires,
        'est_abonne': est_abonne,
    })


@login_required
@require_POST
def toggle_abonnement(request, slug):
    artiste = get_object_or_404(Artiste, slug=slug)
    if artiste.abonnes.filter(pk=request.user.pk).exists():
        artiste.abonnes.remove(request.user)
        return JsonResponse({'abonne': False, 'nb': artiste.nb_abonnes})
    artiste.abonnes.add(request.user)
    return JsonResponse({'abonne': True, 'nb': artiste.nb_abonnes})


@login_required
def mes_playlists(request):
    playlists = Playlist.objects.filter(proprietaire=request.user).annotate(
        nb=Count('titres')
    )
    return render(request, 'music/playlists.html', {'playlists': playlists})


@login_required
def detail_playlist(request, slug):
    playlist = get_object_or_404(Playlist, slug=slug)
    if not playlist.est_publique and playlist.proprietaire != request.user:
        messages.error(request, "Cette playlist est privée.")
        return redirect('accueil')
    items = PlaylistTitre.objects.filter(playlist=playlist).select_related(
        'titre__artiste', 'titre__album'
    ).order_by('ordre')
    return render(request, 'music/playlist.html', {
        'playlist': playlist, 'items': items,
        'est_proprio': playlist.proprietaire == request.user,
    })


@login_required
def creer_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST, request.FILES)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.proprietaire = request.user
            playlist.save()
            messages.success(request, f"Playlist « {playlist.nom} » créée !")
            return redirect('detail_playlist', slug=playlist.slug)
    else:
        form = PlaylistForm()
    return render(request, 'music/creer_playlist.html', {'form': form})


@login_required
@require_POST
def ajouter_a_playlist(request):
    data = json.loads(request.body)
    titre = get_object_or_404(Titre, pk=data.get('titre_id'))
    playlist = get_object_or_404(Playlist, pk=data.get('playlist_id'), proprietaire=request.user)
    ordre = playlist.titres.count()
    PlaylistTitre.objects.get_or_create(playlist=playlist, titre=titre, defaults={'ordre': ordre})
    return JsonResponse({'ok': True, 'message': f"Ajouté à « {playlist.nom} »"})


@login_required
@require_POST
def retirer_de_playlist(request, playlist_slug, titre_pk):
    playlist = get_object_or_404(Playlist, slug=playlist_slug, proprietaire=request.user)
    PlaylistTitre.objects.filter(playlist=playlist, titre_id=titre_pk).delete()
    return JsonResponse({'ok': True})


@login_required
def profil(request):
    historique = Historique.objects.filter(
        utilisateur=request.user
    ).select_related('titre__artiste')[:20]
    playlists = Playlist.objects.filter(proprietaire=request.user)
    return render(request, 'music/profil.html', {
        'historique': historique,
        'playlists': playlists,
    })


@login_required
def recherche_deezer(request):
    q = request.GET.get('q', '').strip()
    resultats = []
    if q:
        url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}&limit=20"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                resultats = data.get('data', [])
        except Exception:
            pass
    return render(request, 'music/deezer.html', {'q': q, 'resultats': resultats})


@login_required
def artiste_deezer(request, artiste_id):
    try:
        url = f"https://api.deezer.com/artist/{artiste_id}/top?limit=20"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read())
            titres = data.get('data', [])
        url2 = f"https://api.deezer.com/artist/{artiste_id}"
        with urllib.request.urlopen(url2) as response2:
            artiste = json.loads(response2.read())
    except Exception:
        titres, artiste = [], {}
    return render(request, 'music/deezer_artiste.html', {'titres': titres, 'artiste': artiste})
@login_required
def playlists_deezer(request):
    playlists_genres = {
        'Hip-Hop 🎤': 116,
        'Afrobeats 🌍': 2309,
        'R&B 🎶': 15,
        'Pop ⭐': 132,
        'Rock 🎸': 152,
        'Jazz 🎷': 129,
        'Electronique 🎧': 106,
        'Reggae 🌿': 144,
    }

    playlists = {}
    for genre_nom, genre_id in playlists_genres.items():
        url = f"https://api.deezer.com/chart/{genre_id}/tracks?limit=15"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                playlists[genre_nom] = data.get('data', [])
        except Exception:
            playlists[genre_nom] = []

    return render(request, 'music/playlists_deezer.html', {'playlists': playlists})
@login_required
def tendances(request):
    tops = {}
    pays = {
        'Monde 🌍': 0,
        'France 🇫🇷': 'fr',
        'Nigeria 🇳🇬': 'ng',
        'USA 🇺🇸': 'us',
        'Cameroun 🇨🇲': 'cm',
        'Congo 🇨🇬': 'cg',
        'Côte d\'Ivoire 🇨🇮': 'ci',
        'Sénégal 🇸🇳': 'sn',
    }
    for pays_nom, pays_code in pays.items():
        if pays_code == 0:
            url = "https://api.deezer.com/chart/0/tracks?limit=10"
        else:
            url = f"https://api.deezer.com/chart/0/tracks?limit=10&country={pays_code}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                tops[pays_nom] = data.get('data', [])
        except Exception:
            tops[pays_nom] = []

    return render(request, 'music/tendances.html', {'tops': tops})
@login_required
@require_POST
def toggle_like_deezer(request):
    data = json.loads(request.body)
    deezer_id = str(data.get('deezer_id'))
    titre = data.get('titre', '')
    artiste = data.get('artiste', '')
    cover = data.get('cover', '')
    preview = data.get('preview', '')
    duree = data.get('duree', 0)

    from .models import LikeDeezer
    like, created = LikeDeezer.objects.get_or_create(
        utilisateur=request.user,
        deezer_id=deezer_id,
        defaults={
            'titre': titre,
            'artiste': artiste,
            'cover': cover,
            'preview': preview,
            'duree': duree,
        }
    )
    if not created:
        like.delete()
        return JsonResponse({'liked': False})
    return JsonResponse({'liked': True})
@login_required
def mes_likes_deezer(request):
    from .models import LikeDeezer
    likes = LikeDeezer.objects.filter(utilisateur=request.user)
    return render(request, 'music/likes_deezer.html', {'likes': likes})
@login_required
def commentaires_artiste(request, artiste_id):
    from .models import CommentaireDeezer
    
    # Récupérer les infos de l'artiste depuis Deezer
    artiste = {}
    try:
        url = f"https://api.deezer.com/artist/{artiste_id}"
        with urllib.request.urlopen(url) as response:
            artiste = json.loads(response.read())
    except Exception:
        pass

    # Ajouter un commentaire
    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        note = request.POST.get('note', 5)
        if contenu:
            CommentaireDeezer.objects.create(
                utilisateur=request.user,
                deezer_artiste_id=str(artiste_id),
                artiste_nom=artiste.get('name', ''),
                contenu=contenu,
                note=int(note),
            )
            messages.success(request, "Commentaire ajouté !")
            return redirect('commentaires_artiste', artiste_id=artiste_id)

    commentaires = CommentaireDeezer.objects.filter(
        deezer_artiste_id=str(artiste_id)
    ).select_related('utilisateur')

    # Calculer la note moyenne
    note_moyenne = 0
    if commentaires:
        note_moyenne = sum(c.note for c in commentaires) / len(commentaires)

    return render(request, 'music/commentaires_artiste.html', {
        'artiste': artiste,
        'commentaires': commentaires,
        'note_moyenne': round(note_moyenne, 1),
        'artiste_id': artiste_id,
    })


@login_required
@require_POST
def supprimer_commentaire(request, commentaire_id):
    from .models import CommentaireDeezer
    commentaire = get_object_or_404(CommentaireDeezer, pk=commentaire_id, utilisateur=request.user)
    artiste_id = commentaire.deezer_artiste_id
    commentaire.delete()
    messages.success(request, "Commentaire supprimé !")
    return redirect('commentaires_artiste', artiste_id=artiste_id)