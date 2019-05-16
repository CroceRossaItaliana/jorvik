from .models import AssenzaCorsoBase


class GestioneAssenza:
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
