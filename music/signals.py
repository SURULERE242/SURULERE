from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import ProfilUtilisateur, Titre


@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        ProfilUtilisateur.objects.get_or_create(utilisateur=instance)


@receiver(post_save, sender=Titre)
def lire_duree_audio(sender, instance, created, **kwargs):
    if created and instance.duree == 0 and instance.fichier_audio:
        try:
            from mutagen import File as MutagenFile
            audio = MutagenFile(instance.fichier_audio.path)
            if audio and audio.info:
                duree = int(audio.info.length)
                Titre.objects.filter(pk=instance.pk).update(duree=duree)
        except ImportError:
            pass
        except Exception:
            pass