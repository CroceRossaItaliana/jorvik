from django.core.management import BaseCommand

from anagrafica.models import Persona, Appartenenza
from datetime import date


class Command(BaseCommand):
    help = 'cancella data fine apparteneze future in caso di volontario in estensione'

    def handle(self, *args, **options):
        today = date.today()
        appartenenze=Appartenenza.objects.filter(membro=Appartenenza.ESTESO)
        for appartenenza in appartenenze:
            print(appartenenza.membro)
            if appartenenza.fine is not None and today < appartenenza.fine.date():
                appartenenza_obj = Appartenenza.objects.get(id=appartenenza.pk)
                appartenenza_obj.save()

        self.stdout.write(self.style.SUCCESS('Eliminate le date di appartenenze future di volontario in estensione'))
