from django.shortcuts import redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages

from base.files import Zip
from .models import AssenzaCorsoBase


class GestionePresenza:
    def __init__(self, request, lezione, me, partecipanti):
        self.request = request
        self.lezione = lezione
        self.me = me

        self._verifica_presenze(partecipanti)

    @property
    def presenze_lezione(self):
        return self.request.POST.getlist('presenze-%s' % self.lezione.pk)

    def get_esonero(self):
        key = 'esonero-%s-%s' % (self.lezione.pk, self.partecipante.pk)
        return self.request.POST.get(key)

    @property
    def esonero_checkbox(self):
        key = 'esonero-checkbox-%s-%s' % (self.lezione.pk, self.partecipante.pk)
        return self.request.POST.get(key)

    def _process_presenza(self):
        if not self.esonero or self.esonero_checkbox != 'on':
            # Se non è esonero - elimina oggetti <Assenza> (è presente)
            q = AssenzaCorsoBase.objects.filter(lezione=self.lezione,
                                                persona=self.partecipante)
            q.delete()
            self.esonero = None

    def _process_assenza(self):
        # Assenza "ESONERO" ha un valore, ma la persona è segnata come assente
        if self.esonero:
            # Trova assenze che possono avere "esonero"
            assenza = AssenzaCorsoBase.objects.filter(lezione=self.lezione,
                                                      persona=self.partecipante)
            if assenza.exists():
                # Rimuovi "esonero" e fai oggetto come semplice assenza
                assenza.update(esonero=False, esonero_motivazione=None)
        # Assenza (senza esonero)
        else:
            assenza = AssenzaCorsoBase.create_assenza(self.lezione,
                                                      self.partecipante,
                                                      self.me)

        # Per non procedere alla lavorazione dell'esonero (il codice sotto)
        self.esonero = None

    def _process_esonero(self):
        assenza = AssenzaCorsoBase.create_assenza(self.lezione,
            self.partecipante, self.me, esonero=self.esonero)
        return assenza

    def _verifica_presenze(self, partecipanti):
        for partecipante in partecipanti:
            self.partecipante = partecipante
            self.esonero = self.get_esonero()

            if "%s" % partecipante.pk in self.presenze_lezione:
                self._process_presenza()
            else:
                self._process_assenza()

            if self.esonero:  # Campo "Esonero" Valorizzato (impostata una motivazione)
                self._process_esonero()


class GeneraReport:
    ATTESTATO_FILENAME = "%s - Attestato.pdf"
    SCHEDA_FILENAME = "%s - Scheda di Valutazione.pdf"

    def __init__(self, request, corso, single_attestato=False):
        self.request = request
        self.corso = corso

    def download(self):
        """ Returns a HTTP response """

        self.archive = Zip(oggetto=self.corso)

        if self.request.GET.get('download_single_attestato'):
            return self._download_single_attestato()
        else:
            self._generate()
            self.archive.comprimi_e_salva(nome="Corso %d-%d.zip" % (self.corso.progressivo,
                                                                    self.corso.anno))
            return redirect(self.archive.download_url)

    def _download_single_attestato(self):
        from .models import PartecipazioneCorsoBase
        from curriculum.models import Titolo

        try:
            partecipazione = self.corso.partecipazioni_confermate().get(
            titolo_ottenuto__pk=self.request.GET.get('download_single_attestato'),
            persona=self.request.user.persona)
        except PartecipazioneCorsoBase.DoesNotExist:
            messages.error(self.request, "Questo attestato non esiste.")
            return redirect(reverse('utente:cv_tipo', args=[Titolo.TITOLO_CRI,]))

        attestato = self._attestato(partecipazione)
        filename = self.ATTESTATO_FILENAME % partecipazione.titolo_ottenuto.last()

        with open(attestato.file.path, 'rb') as f:
            pdf = f.read()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % '-'.join(filename.split())
        response.write(pdf)
        return response

    def _generate(self):
        for partecipante in self.corso.partecipazioni_confermate():
            self._schede(partecipante)

            if partecipante.idoneo:  # Se idoneo, genera l'attestato
                self._attestato(partecipante)

    def _schede(self, partecipante):
        """ Genera la scheda di valutazione """

        scheda = partecipante.genera_scheda_valutazione()
        self.archive.aggiungi_file(
            scheda.file.path,
            self.SCHEDA_FILENAME % partecipante.persona.nome_completo
        )
        return scheda

    def _attestato(self, partecipante):
        attestato = partecipante.genera_attestato()
        self.archive.aggiungi_file(
            attestato.file.path,
            self.ATTESTATO_FILENAME % partecipante.persona.nome_completo
        )
        return attestato
