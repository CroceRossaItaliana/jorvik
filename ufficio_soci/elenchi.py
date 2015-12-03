from anagrafica.models import Persona, Appartenenza


class Elenco:
    """
    Rappresenta un elenco semplice di persone.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def modulo(self):
        """
        Ritorna un oggetto forms.Form da compilare.
        :return:
        """
        return None

    def risultati(self, modulo=None):
        """
        Dato il contenuto del modulo.
        :param modulo:
        :param args:
        :param kwargs:
        :return: Un QuerySet<Persona> con tutti i risultati.
        """
        raise NotImplementedError("Metodo risultati dell'elenco non implementato.")

    def ordina(self, qs):
        return qs

    def excel_colonne(self):
        return ()

    def excel_foglio(self, p):
        """
        Questa funzione, data una persona, determina in quale foglio excel
         dell'elenco verra' posizionato.
        :param p: La persona.
        :return: Il nome del foglio di destinazione.
        """
        return "Foglio 1"

    def template(self):
        return 'us_elenchi_inc_vuoto.html'


class ElencoSemplice(Elenco):

    def excel_colonne(self):
        return super(ElencoSemplice, self).excel_colonne() + (
            ("Cognome", lambda p: p.cognome),
            ("Nome", lambda p: p.nome),
            ("Codice Fiscale", lambda p: p.codice_fiscale),
        )

    def template(self):
        return 'us_elenchi_inc_persone.html'

    def ordina(self, qs):
        return qs.order_by('cognome', 'nome',)


class ElencoSoci(ElencoSemplice):
    """
    args: QuerySet<Sede>
    """

    def risultati(self, modulo=None):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_SOCIO,
            ).via("appartenenze")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )

    def template(self):
        return 'us_elenchi_inc_soci.html'

    def excel_foglio(self, p):
        return p.sedi_attuali(membro__in=Appartenenza.MEMBRO_SOCIO).first().nome

    def excel_colonne(self):
        return super(ElencoSoci, self).excel_colonne() + (
            ("Data di Nascita", lambda p: p.data_nascita),
            ("Luogo di Nascita", lambda p: p.comune_nascita),
            ("Provincia di Nascita", lambda p: p.provincia_nascita),
            ("Stato di Nascita", lambda p: p.stato_nascita),
            ("Indirizzo di residenza", lambda p: p.indirizzo_residenza),
            ("Comune di residenza", lambda p: p.comune_residenza),
            ("Provincia di residenza", lambda p: p.provincia_residenza),
            ("Stato di residenza", lambda p: p.stato_residenza),
            ("Email", lambda p: p.email),
            ("Numeri di telefono", lambda p: ", ".join([str(x) for x in p.numeri_telefono.all()])),
            ("Ingresso in CRI", lambda p: p.ingresso())
        )
