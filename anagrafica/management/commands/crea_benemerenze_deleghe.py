from django.core.management import BaseCommand

from anagrafica.models import Sede
from anagrafica.models import Persona
from anagrafica.models import Delega
from anagrafica.permessi.applicazioni import ISPETTRICE_IIVV, ISPETTORE_CM, OFFICER_PRESIDENZA
from anagrafica.permessi.applicazioni import PRESIDENTE_COMMISSIONE, MEMBRO_COMMISSIONE
from anagrafica.permessi.applicazioni import SEGRETARIO_GENERALE, ISPETTORE
from base.utils import poco_fa


class Command(BaseCommand):

    def handle(self, *args, **options):

        deleghe = [
            {'userid': 82683, 'sede': 1136, 'tipo': ISPETTORE_CM, 'firma': 54698},
            {'userid': 112954, 'sede': 1136, 'tipo': ISPETTRICE_IIVV, 'firma': 54698},
            {'userid': 201324, 'sede': 1136, 'tipo': ISPETTORE, 'firma': 54698},
            {'userid': 108842, 'sede': 1105, 'tipo': ISPETTORE, 'firma': 27897},
            {'userid': 8350, 'sede': 1105, 'tipo': OFFICER_PRESIDENZA, 'firma': 27897},
            {'userid': 34028, 'sede': 1105,
                'tipo': OFFICER_PRESIDENZA, 'firma': 27897},
            {'userid': 23889, 'sede': 1105,
                'tipo': OFFICER_PRESIDENZA, 'firma': 27897},
            {'userid': 41127, 'sede': 1105, 'tipo': ISPETTRICE_IIVV, 'firma': 27897},
            {'userid': 8731, 'sede': 1105, 'tipo': ISPETTORE, 'firma': 27897},
            {'userid': 22193, 'sede': 1, 'tipo': OFFICER_PRESIDENZA, 'firma': 82741},
            {'userid': 220863, 'sede': 1, 'tipo': OFFICER_PRESIDENZA, 'firma': 82741},
            {'userid': 23119, 'sede': 1, 'tipo': PRESIDENTE_COMMISSIONE, 'firma': 82741},
            {'userid': 82728, 'sede': 1, 'tipo': MEMBRO_COMMISSIONE, 'firma': 82741},
            {'userid': 55920, 'sede': 1, 'tipo': MEMBRO_COMMISSIONE, 'firma': 82741},
            {'userid': 2937, 'sede': 1, 'tipo': SEGRETARIO_GENERALE, 'firma': 82741},
            {'userid': 320303, 'sede': 1, 'tipo': OFFICER_PRESIDENZA, 'firma': 82741},
            {'userid': 266562, 'sede': 1, 'tipo': ISPETTORE, 'firma': 82741},
            {'userid': 3254, 'sede': 1, 'tipo': ISPETTRICE_IIVV, 'firma': 82741},
        ]

        for d in deleghe:
            persona = Persona.objects.get(pk=d['userid'])
            me = Persona.objects.get(pk=d['firma'])
            sede = Sede.objects.get(pk=d['sede'])
            nomina = d['tipo']

            delega = Delega(
                persona=persona,
                tipo=nomina,
                oggetto=sede,
                inizio=poco_fa(),
                firmatario=me,
            )

            print('Creata delega per {} su {} di tipo {}'.format(
                persona, sede, nomina
            ))

            delega.save()
