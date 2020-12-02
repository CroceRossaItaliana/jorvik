from anagrafica.models import Trasferimento
from posta.models import Messaggio
from ..errori import errore_generico


class AutorizzazioneProcess:
    def __init__(self, request, me, pk):
        from django.shortcuts import get_object_or_404
        from anagrafica.models import Autorizzazione

        self.request = request
        self.me = me
        self.pk = pk

        self.richiesta = get_object_or_404(Autorizzazione, pk=self.pk)
        self.form = None
        self._autorizzazione_form = None

    def concedi(self):
        """ Mostra il modulo da compilare per il consenso,
        ed eventualmente registra l'accettazione. """

        self._template = 'base_autorizzazioni_concedi.html'
        self._autorizzazione_form = self.richiesta.oggetto.autorizzazione_concedi_modulo()
        return self._process(concedi=True)

    def nega(self):
        """ Mostra il modulo da compilare per la negazione,
        ed eventualmente registra la negazione. """

        self._template = 'base_autorizzazioni_nega.html'
        self._autorizzazione_form = self.richiesta.oggetto.autorizzazione_nega_modulo()
        return self._process(concedi=False)

    def _process(self, concedi):
        richiesta = self.richiesta

        if self._validate() is not None:
            return self._validate()

        if self._autorizzazione_form is not None:
            self._process_form(concedi)  # Se la richiesta ha un modulo di consenso
        else:
            # Accetta la richiesta senza modulo
            if concedi:
                richiesta.concedi(self.me)
            else:
                richiesta.nega(self.me)

        context = {
            "richiesta": richiesta,
            "modulo": self.form,
            "torna_url": self.torna_url,
        }

        return self._template, context

    def _form_kwargs(self):
        """
        kwargs da passare nella form da validare.
        :return: empty dict (default) or dict with kwargs.
        """

        try:
            if self.richiesta.oggetto is not None:
                return dict(instance=self.richiesta.oggetto)
        except Exception as e:
            return dict()
        return dict()

    def _process_form(self, concedi):
        form_kwargs = self._form_kwargs()

        if self.request.POST:
            try:
                self.form = self._autorizzazione_form(self.request.POST, **form_kwargs)
            except TypeError:
                # Per evitare __init__() got an unexpected keyword argument 'instance'
                self.form = self._autorizzazione_form(self.request.POST)

            if self.form.is_valid():
                # Accetta la richiesta con modulo
                if concedi:
                    self.richiesta.concedi(self.me, modulo=self.form)
                else:
                    self.richiesta.nega(self.me, modulo=self.form)

                if isinstance(self.richiesta.oggetto, Trasferimento):
                    destinatari = [self.richiesta.oggetto.destinazione.sede_regionale.presidente()]
                    destinatari.extend(self.richiesta.oggetto.destinazione.sede_regionale.delegati_ufficio_soci())
                    Messaggio.costruisci_e_accoda(
                        oggetto="Trasferimento {}".format("Confermato" if concedi else "Negato"),
                        modello="email_richiesta_trasferimento_regionale.html",
                        corpo={
                            "persona": self.richiesta.oggetto.richiedente.nome_completo,
                            "comitato": self.richiesta.oggetto.destinazione,
                            "stato": "Confermata" if concedi else "Negata"
                        },
                        destinatari=set(destinatari),
                    )
        else:
            try:
                self.form = self._autorizzazione_form(**form_kwargs)
            except TypeError:
                # Per evitare __init__() got an unexpected keyword argument 'instance'
                self.form = self._autorizzazione_form()

    def _validate(self):
        self.torna_url = self.request.session.get('autorizzazioni_torna_url',
                                                  default="/autorizzazioni/")

        # Controlla che io possa firmare questa autorizzazione
        if not self.me.autorizzazioni_in_attesa().filter(pk=self.richiesta.pk).exists():
            return self._richiesta_non_trovata

        # from formazione.models import PartecipazioneCorsoBase
        # if not PartecipazioneCorsoBase.controlla_richiesta_processabile(self.richiesta):
        #     return self._richiesta_non_processabile

    @property
    def _richiesta_non_trovata(self):
        return errore_generico(self.request, self.me,
           titolo="Richiesta non trovata",
           messaggio="E' possibile che la richiesta sia stata già approvata o respinta da qualcun altro.",
           torna_titolo="Richieste in attesa",
           torna_url=self.torna_url,
       )

    @property
    def _richiesta_non_processabile(self):
        return errore_generico(self.request, self.me,
            titolo="Richiesta non processabile",
            messaggio="Questa richiesta non può essere processata.",
            torna_titolo="Richieste in attesa",
            torna_url=self.torna_url,
        )
