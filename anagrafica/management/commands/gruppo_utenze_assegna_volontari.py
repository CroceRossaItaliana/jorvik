from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from anagrafica.models import Appartenenza, Sede
from autenticazione.models import Utenza


class Command(BaseCommand):

    NOME_GRUPPO = 'Assemblea di Matera'

    help = 'Creare ilo grupppo {} ed assegna i volontario di comitato di Matera'.format(NOME_GRUPPO)

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
        comitato = 'Comitato di Matera'
        vo_cm = []
        nr = 1
        sede = Sede.objects.filter(nome=comitato).first()
        volontari = sede.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, figli=True, fine__isnull=True)
        utenza = None
        for appartenenza in volontari:
            persona = appartenenza.persona
            try:
                utenza = persona.utenza
                # utenza = Utenza.objects.filter(persona=persona).order_by('last_login').first()
                # print(nr, utenza.persona.nome, utenza.persona.cognome)
                utenza.groups.add(gruppo)
                utenza.save()
                nr += 1
                vo_cm.append(utenza)
            except Utenza.DoesNotExist:
                pass

        print(vo_cm)
        print(
            'distinct persone', len(vo_cm), '\n'
        )

    def handle(self, *args, **options):

        self._crea_gruppo_aggancia_utenti()

        if options['clean']:
            if options['clean'] == 'clean':
                msg = "Gruppo {} eliminato".format(self.NOME_GRUPPO) \
                    if self._elimina_gruppo() else "Gruppo {} inesistente".format(self.NOME_GRUPPO)
                print(msg)
            else:
                print('Argomento {} inesistente'.format(options['clean']))
        else:
            self._crea_gruppo_aggancia_utenti()
