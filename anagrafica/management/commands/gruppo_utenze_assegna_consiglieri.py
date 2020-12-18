from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE
from anagrafica.models import Sede
from anagrafica.permessi.applicazioni import CONSIGLIERE_GIOVANE
from autenticazione.models import Utenza


class Command(BaseCommand):

    NOME_GRUPPO = 'Assemblea giovani'

    help = 'Creare il grupppo {} ed assegna dei consiglieri giovani'.format(NOME_GRUPPO)

    def add_arguments(self, parser):
        parser.add_argument('clean', nargs='?', type=str, default='')

    def _elimina_gruppo(self):
        gruppo = Group.objects.filter(name=self.NOME_GRUPPO).first()
        if gruppo:
            gruppo.delete()
            return True
        else:
            return False

    def _crea_gruppo(self):
        msg = "Elimino gruppo {}...".format(self.NOME_GRUPPO) \
            if self._elimina_gruppo() else ""
        print(msg)
        print("Creo gruppo {}...".format(self.NOME_GRUPPO))
        gruppo = Group(name=self.NOME_GRUPPO)
        gruppo.save()
        return gruppo

    def _crea_gruppo_aggancia_utenti(self):
        gruppo = self._crea_gruppo()
        cg = []
        for sede in Sede.objects.filter(attiva=True, estensione__in=[LOCALE, PROVINCIALE, REGIONALE, NAZIONALE]):
            deleghe = sede.deleghe_attuali(tipo=CONSIGLIERE_GIOVANE)
            for delega in deleghe:
                persona = delega.persona
                if persona:
                    if persona not in cg:
                        utenza = Utenza.objects.filter(persona=persona).order_by('last_login').first()
                        if utenza:
                            utenza.groups.add(gruppo)
                            utenza.save()
                            cg.append(persona)
                else:
                    print(delega, persona)
        print(
            'consiglieri giovani aggiunti {}'.format(len(cg))
        )

    def handle(self, *args, **options):
        if options['clean']:
            if options['clean'] == 'clean':
                msg = "Gruppo {} eliminato".format(self.NOME_GRUPPO) \
                    if self._elimina_gruppo() else "Gruppo {} inesistente".format(self.NOME_GRUPPO)
                print(msg)
            else:
                print('Argomento {} inesistente'.format(options['clean']))
        else:
            self._crea_gruppo_aggancia_utenti()
