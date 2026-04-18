from django.contrib import admin
from .models import Genre, Artiste, Album, Titre, Playlist, FavoriTitre, Historique, ProfilUtilisateur


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Artiste)
class ArtisteAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nb_abonnes', 'date_creation']
    search_fields = ['nom']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['titre', 'artiste', 'type_album', 'date_sortie']
    list_filter = ['type_album', 'genre']
    search_fields = ['titre', 'artiste__nom']
    prepopulated_fields = {'slug': ('titre',)}


@admin.register(Titre)
class TitreAdmin(admin.ModelAdmin):
    list_display = ['titre', 'artiste', 'album', 'duree_formattee', 'nb_ecoutes', 'date_ajout']
    list_filter = ['genre', 'est_explicite']
    search_fields = ['titre', 'artiste__nom']
    readonly_fields = ['nb_ecoutes']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['nom', 'proprietaire', 'nb_titres', 'est_publique', 'date_creation']
    list_filter = ['est_publique']
    search_fields = ['nom', 'proprietaire__username']


@admin.register(FavoriTitre)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'titre', 'date_ajout']


@admin.register(Historique)
class HistoriqueAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'titre', 'date_ecoute']
    list_filter = ['date_ecoute']


@admin.register(ProfilUtilisateur)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'abonne_premium', 'date_creation']