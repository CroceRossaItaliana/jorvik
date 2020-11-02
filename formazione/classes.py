from datetime import datetime, timedelta, date

from django.db.models import Q
from django.shortcuts import redirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib import messages

from anagrafica.models import Persona
from anagrafica.permessi.costanti import MODIFICA
from base.files import Zip
from .models import AssenzaCorsoBase, CorsoBase
from .forms import ModuloModificaLezione


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
                                                  self.partecipante,
                                                  self.me,
                                                  esonero=self.esonero)
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
    ATTESTATO_FILENAME = "%s %s - Attestato.pdf"
    SCHEDA_FILENAME = "%s %s - Scheda di Valutazione.pdf"

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
        filename = self.ATTESTATO_FILENAME % (partecipazione.titolo_ottenuto.last(), '')

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

        scheda = partecipante.genera_scheda_valutazione(request=self.request)
        persona = partecipante.persona
        self.archive.aggiungi_file(
            scheda.file.path,
            self.SCHEDA_FILENAME % (persona.cognome, persona.nome)
        )
        return scheda

    def _attestato(self, partecipante):
        attestato = partecipante.genera_attestato(request=self.request)
        persona = partecipante.persona

        self.archive.aggiungi_file(
            attestato.file.path,
            self.ATTESTATO_FILENAME % (persona.cognome, persona.nome)
        )
        return attestato


class GestioneLezioni:
    def __init__(self, request, me, pk, lezione_pk=None):
        self.request = request
        self.me = me
        self.lezione_pk = lezione_pk

        self.created = None  # <LezioneCorsoBase> object
        self.moduli = list()
        self.partecipanti_lezioni = list()
        self.invalid_forms = list()

        self._set_post_actions()

        self.corso = get_object_or_404(CorsoBase, pk=pk)
        self.partecipanti = Persona.objects.filter(
            partecipazioni_corsi__in=self.corso.partecipazioni_confermate()
        ).order_by('cognome')

    def _set_post_actions(self):
        request = self.request
        self.AZIONE_SALVA = request.POST and request.POST['azione'] == 'salva'
        self.AZIONE_SALVA_PRESENZE = request.POST and request.POST['azione'] == 'salva_presenze'
        self.AZIONE_NUOVA = request.POST and request.POST['azione'] == 'nuova'
        self.AZIONE_DIVIDI = request.POST and request.POST['azione'] == 'dividi'

    @property
    def ho_permesso(self):
        if not self.me.permessi_almeno(self.corso, MODIFICA):
            return False
        return True

    @property
    def lezioni(self):
        """
        Restituire tutte le lezioni del corso o solo singola lezione (dalla view save)
        :return: <LezioneCorsoBase> QuerySet
        """

        lezioni = self.corso.lezioni
        q = lezioni.filter(pk=self.lezione_pk) if self.lezione_pk else lezioni.all()
        return q.order_by('inizio', 'fine', 'scheda_lezione_num',)

    def get_partecipanti_senza_esonero(self, lezione):
        return self.partecipanti.exclude(
            Q(assenze_corsi_base__esonero=False),
            assenze_corsi_base__lezione=lezione
        ).order_by('nome', 'cognome')

    def _lezione_form(self, lezione):
        request_data = self.request.POST if (self.AZIONE_SALVA or
                                             self.AZIONE_DIVIDI) else None
        return ModuloModificaLezione(
            request_data,
            instance=lezione,
            prefix="%s" % lezione.pk,
            corso=self.corso,
            initial={
                "inizio": self.corso.data_inizio,
                "fine": self.corso.data_esame
            } if self.corso.online else None
        )

    def presenze_assenze(self, per_singola_lezione=False):
        for lezione in self.lezioni:
            form = self._lezione_form(lezione)

            if self.request.POST:
                if self.AZIONE_SALVA and form.is_valid():
                    form.save()
                else:
                    self.invalid_forms.append(int("%s" % lezione.pk))

            self.moduli += [form]

            # Excludi assenze con esonero
            partecipanti_lezione = self.get_partecipanti_senza_esonero(lezione)

            if self.AZIONE_SALVA:
                GestionePresenza(self.request, lezione, self.me, self.partecipanti)

            self.partecipanti_lezioni += [partecipanti_lezione]

        if self.AZIONE_NUOVA:
            self.new()

    def _instantiate_new_form(self, **kwargs):
        form_args = list()
        form_kwargs = {
            'corso': self.corso,
            'prefix': 'nuova',
        }

        if self.AZIONE_NUOVA:
            form_args.append(self.request.POST)
        else:
            if self.corso.online:
                form_kwargs['initial'] = {
                    "inizio": self.corso.data_inizio,
                    "fine": self.corso.data_esame
                }
            else:
                form_kwargs['initial'] = {
                    "inizio": timezone.now(),
                    "fine": timezone.now() + timedelta(hours=2)
                }
        return ModuloModificaLezione(*form_args, **form_kwargs)

    @property
    def _form_nuova_lezione(self):
        return self._instantiate_new_form()

    def new(self):
        form = self._form_nuova_lezione
        if form.is_valid():
            cd = form.cleaned_data

            lezione = form.save(commit=False)
            lezione.corso = self.corso
            lezione.save()

            lezione.docente = cd['docente']
            if self.corso.online:
                from formazione.training_api import TrainingApi
                api = TrainingApi()
                for docente in cd['docente']:
                    api.aggiugi_ruolo(docente, self.corso, TrainingApi.DOCENTE)

            lezione.save()

            self.avvisare_docente_e_presidente(lezione)

            self.created = lezione

    def save(self):
        """
        Chiamata dalla view <course_lezione_save>

        :return: Se la form è validata - http response object.
        Altrimento non restituisce nulla, saranno restituiti i dati del metodo
        get_http_response() (segui la logica della vista)
        """

        lezione = self.lezioni.get(pk=self.lezione_pk, corso=self.corso)
        form = self._lezione_form(lezione)
        if self.AZIONE_SALVA_PRESENZE:
            GestionePresenza(self.request, lezione, self.me, self.partecipanti)

            messages.success(self.request, "La presenze sono state salvate.")
            return redirect("%s" % self.corso.url_lezioni)

        if form.is_valid() and (self.AZIONE_SALVA or self.AZIONE_DIVIDI):
            form.save()

            if self.AZIONE_DIVIDI:
                # A questo punto la lezione parente ha salvato i dati inseriti
                # nella form e ha creato una nuova lezione figlio
                return self.dividi(lezione)

            self.avvisare_docente_e_presidente(lezione)

            if self.corso.online:
                from formazione.training_api import TrainingApi
                api = TrainingApi()
                for docente in form.cleaned_data['docente']:
                    api.aggiugi_ruolo(docente, self.corso, TrainingApi.DOCENTE)

            messages.success(self.request, "La lezione è stata salvata correttamente.")
            return redirect("%s#%d" % (self.corso.url_lezioni, lezione.pk))
        else:
            self.invalid_forms.append(int("%s" % self.lezione_pk))

        self.moduli += [form]

        # Escludi assenze con esonero
        partecipanti_lezione = self.get_partecipanti_senza_esonero(lezione)

        self.partecipanti_lezioni += [partecipanti_lezione]

    def dividi(self, lezione):
        if not lezione.puo_dividere:
            messages.error(self.request, "Non si può più dividere questa lezione.")
            return redirect(self.corso.url_lezioni)

        lezione.dividi()

        messages.success(self.request, "La lezione è stata divisa. Modifica le date di inizio/fine della nuova lezione")
        return redirect(self.corso.url_lezioni)

    def avvisare_docente_e_presidente(self, lezione):
        # Avvisa docente e il suo presidente della nomina
        lezione.avvisa_docente_nominato_al_corso(self.me)

        # Se non è del comitato che organizza il corso
        lezione.avvisa_presidente_docente_nominato()

    def get_context(self):
        return 'aspirante_corso_base_scheda_lezioni.html', {
            "puo_modificare": True,
            "corso": self.corso,
            "lezioni": zip(self.lezioni, self.moduli, self.partecipanti_lezioni),
            "partecipanti": self.partecipanti,
            "modulo_nuova_lezione": self._form_nuova_lezione,
            'invalid_forms': self.invalid_forms,
        }

    def get_http_response(self):
        if self.created:  # set in new()
            messages.success(self.request, "La lezione è stata creata correttamente.")
            return redirect("%s#%d" % (self.corso.url_lezioni, self.created.pk))

        return self.get_context()
