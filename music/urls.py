from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('inscription/', views.inscription, name='inscription'),
    path('login/', views.connexion, name='connexion'),
    path('logout/', views.deconnexion, name='deconnexion'),

    # Pages
    path('', views.accueil, name='accueil'),
    path('explorer/', views.explorer, name='explorer'),
    path('recherche/', views.recherche, name='recherche'),
    path('profil/', views.profil, name='profil'),

    # Titres
    path('titre/<int:pk>/', views.detail_titre, name='detail_titre'),
    path('titre/ajouter/', views.ajouter_titre, name='ajouter_titre'),
    path('titre/<int:pk>/ecoute/', views.enregistrer_ecoute, name='enregistrer_ecoute'),
    path('titre/<int:pk>/favori/', views.toggle_favori, name='toggle_favori'),
    path('favoris/', views.mes_favoris, name='mes_favoris'),

    # Albums
    path('album/<slug:slug>/', views.detail_album, name='detail_album'),

    # Artistes
    path('artiste/<slug:slug>/', views.detail_artiste, name='detail_artiste'),
    path('artiste/<slug:slug>/abonnement/', views.toggle_abonnement, name='toggle_abonnement'),

    # Playlists
    path('playlists/', views.mes_playlists, name='mes_playlists'),
    path('playlist/<slug:slug>/', views.detail_playlist, name='detail_playlist'),
    path('playlist/creer/', views.creer_playlist, name='creer_playlist'),
    path('playlist/ajouter/', views.ajouter_a_playlist, name='ajouter_a_playlist'),
    path('playlist/<slug:playlist_slug>/retirer/<int:titre_pk>/', views.retirer_de_playlist, name='retirer_de_playlist'),
    path('deezer/', views.recherche_deezer, name='recherche_deezer'),
    path('deezer/artiste/<int:artiste_id>/', views.artiste_deezer, name='artiste_deezer'),
    path('playlists-deezer/', views.playlists_deezer, name='playlists_deezer'),
    path('tendances/', views.tendances, name='tendances'),
    path('likes-deezer/', views.mes_likes_deezer, name='mes_likes_deezer'),
    path('likes-deezer/toggle/', views.toggle_like_deezer, name='toggle_like_deezer'),]