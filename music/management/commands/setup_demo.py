from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from music.models import Genre, Artiste, ProfilUtilisateur
import datetime

GENRES = ['Pop', 'Hip-Hop', 'R&B', 'Électronique', 'Jazz', 'Rock', 'Afrobeat', 'Reggae']

ARTISTES = [
    {'nom': 'Luna Rosa', 'bio': 'Chanteuse indie-pop aux sonorités envoûtantes.'},
    {'nom': 'The Wavemakers', 'bio': 'Groupe électro-rock expérimental de Paris.'},
    {'nom': 'Océan', 'bio': 'Artiste solo ambient et downtempo.'},
]


class Command(BaseCommand):
    help = 'Initialise des données de démonstration'

    def handle(self, *args, **options):
        self.stdout.write('🎵 Création des genres...')
        for g in GENRES:
            Genre.objects.get_or_create(nom=g, defaults={'slug': slugify(g)})
            self.stdout.write(f'  ✓ {g}')

        self.stdout.write('🎤 Création des artistes...')
        for a in ARTISTES:
            slug = slugify(a['nom'])
            artiste, created = Artiste.objects.get_or_create(
                slug=slug,
                defaults={'nom': a['nom'], 'bio': a['bio']}
            )
            if created:
                self.stdout.write(f'  ✓ {artiste.nom}')

        self.stdout.write('👤 Création utilisateur demo...')
        if not User.objects.filter(username='demo').exists():
            user = User.objects.create_user('demo', 'demo@wavefx.com', 'demo1234')
            ProfilUtilisateur.objects.create(utilisateur=user)
            self.stdout.write('  ✓ demo / demo1234')
        else:
            self.stdout.write('  (déjà existant)')

        self.stdout.write(self.style.SUCCESS('\n✅ Données de démo créées !'))