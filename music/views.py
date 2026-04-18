@login_required
def accueil(request):
    titres_populaires = Titre.objects.order_by('-nb_ecoutes')[:10]
    albums_recents = Album.objects.order_by('-date_sortie')[:8]
    artistes = Artiste.objects.annotate(nb_titres=Count('titres')).order_by('-nb_titres')[:8]
    playlists_user = Playlist.objects.filter(proprietaire=request.user)[:5]
    historique = Historique.objects.filter(utilisateur=request.user).select_related('titre__artiste')[:5]

    # Artistes populaires depuis Deezer
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
Ensuite remplace aussi la fonction explorer par :
python@login_required
def explorer(request):
    genres = Genre.objects.annotate(nb=Count('titre')).order_by('-nb')
    artistes = Artiste.objects.annotate(nb=Count('titres')).order_by('-nb')[:12]
    albums = Album.objects.order_by('-date_sortie')[:12]

    # Tops Deezer
    tops_deezer = {}
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
    except Exception:
        pass

    return render(request, 'music/explorer.html', {
        'genres': genres,
        'artistes': artistes,
        'albums': albums,
        'tops_deezer': tops_deezer,
    })