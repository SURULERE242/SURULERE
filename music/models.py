from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Genre(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Genre"
        ordering = ['nom']


class Artiste(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='artiste')
    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='artistes/', blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True)
    abonnes = models.ManyToManyField(User, related_name='artistes_suivis', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    @property
    def nb_abonnes(self):
        return self.abonnes.count()

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Artiste"
        ordering = ['nom']


class Album(models.Model):
    TYPE_CHOICES = [('album', 'Album'), ('ep', 'EP'), ('single', 'Single')]
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    artiste = models.ForeignKey(Artiste, on_delete=models.CASCADE, related_name='albums')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    date_sortie = models.DateField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    type_album = models.CharField(max_length=10, choices=TYPE_CHOICES, default='album')
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.artiste.nom}-{self.titre}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} - {self.artiste.nom}"

    class Meta:
        verbose_name = "Album"
        ordering = ['-date_sortie']


class Titre(models.Model):
    titre = models.CharField(max_length=200)
    artiste = models.ForeignKey(Artiste, on_delete=models.CASCADE, related_name='titres')
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='titres')
    fichier_audio = models.FileField(upload_to='audio/')
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    duree = models.PositiveIntegerField(help_text="Durée en secondes", default=0)
    numero_piste = models.PositiveIntegerField(default=1)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    paroles = models.TextField(blank=True)
    nb_ecoutes = models.PositiveIntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)
    est_explicite = models.BooleanField(default=False)

    @property
    def duree_formattee(self):
        m, s = divmod(self.duree, 60)
        return f"{m}:{s:02d}"

    @property
    def cover_url(self):
        if self.cover:
            return self.cover.url
        if self.album and self.album.cover:
            return self.album.cover.url
        return None

    def __str__(self):
        return f"{self.titre} - {self.artiste.nom}"

    class Meta:
        verbose_name = "Titre"
        ordering = ['album', 'numero_piste', 'titre']


class Playlist(models.Model):
    nom = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    titres = models.ManyToManyField(Titre, through='PlaylistTitre', blank=True)
    cover = models.ImageField(upload_to='playlists/', blank=True, null=True)
    description = models.TextField(blank=True)
    est_publique = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.proprietaire.username}-{self.nom}")
        super().save(*args, **kwargs)

    @property
    def nb_titres(self):
        return self.titres.count()

    @property
    def duree_totale(self):
        total = sum(t.duree for t in self.titres.all())
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f"{h}h {m}min"
        return f"{m}min {s}s"

    def __str__(self):
        return f"{self.nom} ({self.proprietaire.username})"

    class Meta:
        verbose_name = "Playlist"
        ordering = ['-date_modification']


class PlaylistTitre(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    titre = models.ForeignKey(Titre, on_delete=models.CASCADE)
    ordre = models.PositiveIntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre']
        unique_together = ['playlist', 'titre']


class FavoriTitre(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris_titres')
    titre = models.ForeignKey(Titre, on_delete=models.CASCADE, related_name='favoris')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['utilisateur', 'titre']


class Historique(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historique')
    titre = models.ForeignKey(Titre, on_delete=models.CASCADE)
    date_ecoute = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_ecoute']

    def __str__(self):
        return f"{self.utilisateur.username} → {self.titre.titre}"


class ProfilUtilisateur(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    genres_favoris = models.ManyToManyField(Genre, blank=True)
    abonne_premium = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"


class LikeDeezer(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_deezer')
    deezer_id = models.CharField(max_length=50)
    titre = models.CharField(max_length=200)
    artiste = models.CharField(max_length=200)
    cover = models.URLField(blank=True)
    preview = models.URLField(blank=True)
    duree = models.PositiveIntegerField(default=0)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['utilisateur', 'deezer_id']
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.utilisateur.username} ❤ {self.titre}"