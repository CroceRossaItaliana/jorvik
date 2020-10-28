from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE
from anagrafica.models import Sede, Delega
from anagrafica.permessi.applicazioni import PRESIDENTE, COMMISSARIO
from autenticazione.models import Utenza


class Command(BaseCommand):

    NOME_GRUPPO = 'Assemblea'

    help = 'Closes the specified poll for voting'

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
        presidenti = 0
        commissari = 0
        presidenti_commissari = 0
        pr_cm = []
        for sede in Sede.objects.filter(attiva=True, estensione__in=[LOCALE, PROVINCIALE, REGIONALE, NAZIONALE]):
            persona = sede.presidente()
            if persona:
                if persona not in pr_cm:
                    utenza = Utenza.objects.filter(persona=persona).order_by('last_login').first()
                    utenza.groups.add(gruppo)
                    utenza.save()
                    pr_cm.append(persona)

                    if persona.is_presidente and persona.is_comissario:
                        presidenti_commissari += 1
                    elif persona.is_comissario:
                        commissari += 1
                    elif persona.is_presidente:
                        presidenti += 1

        print(
            'distinct persone', len(pr_cm), '\n'
            'presidenti', presidenti, '\n'
            'commissari', commissari, '\n'
            'presidenti_commissari', presidenti_commissari, '\n'
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
