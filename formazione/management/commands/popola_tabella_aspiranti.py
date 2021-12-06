from django.core.management import BaseCommand
import codecs, csv, datetime

from formazione.models import Aspirante, Aspiranti2014_2019, CorsoBase

class Command(BaseCommand):
    help = 'popola aspiranti 2014-2019'

    def handle(self, *args, **options):
        start_date = datetime.datetime(2014, 1, 1, 0, 0, 0)
        end_date = datetime.datetime(2019, 12, 31, 23, 59, 59)

        aspiranti=Aspirante.objects.filter(creazione__range=(start_date, end_date))
        if len(Aspiranti2014_2019.objects.all()) > 0:
            return self.stdout.write(self.style.SUCCESS('La tabella risulta popolata'))

        ids_aspiranti=[]
        for i in aspiranti:
            ids_aspiranti.append(i.pk)

        corso=CorsoBase.objects.all()
        ids_partecipazioni_confermate=[]
        for i in corso:
            if len(i.partecipazioni_confermate())>0:
                for part in i.partecipazioni_confermate():
                    ids_partecipazioni_confermate.append(part.pk)

        aspiranti_giusti=[]
        for i in ids_aspiranti:
            if i not in ids_partecipazioni_confermate:
                aspiranti_giusti.append(i)

        for i in aspiranti_giusti:
            asp = aspiranti.filter(pk=i).first()
            aspirante_record = Aspiranti2014_2019(nome=asp.persona.nome, cognome=asp.persona.cognome, email=asp.persona.email,
                                     persona_id=asp.persona)
            aspirante_record.save()

        print(len(aspiranti_giusti))
        self.stdout.write(self.style.SUCCESS('Popolata la tabella aspiranti 2014-2019 correttamente'))