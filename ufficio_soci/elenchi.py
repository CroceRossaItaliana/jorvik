from django.contrib.admin import ModelAdmin

from anagrafica.models import Persona, Appartenenza
from base.utils import filtra_queryset
from ufficio_soci.forms import ModuloElencoSoci


class Elenco:
    """
    Rappresenta un elenco semplice di persone.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.modulo_riempito = None  # Qui andra' un eventuale modulo riempito.

    def modulo(self):
        """
        Ritorna un oggetto forms.Form da compilare.
        :return:
        """
        return None

    def risultati(self):
        """
        Dato il contenuto del modulo.
        :param modulo:
        :param args:
        :param kwargs:
        :return: Un QuerySet<Persona> con tutti i risultati.
        """
        raise NotImplementedError("Metodo risultati dell'elenco non implementato.")

    def filtra(self, queryset, termine):
        raise NotImplementedError("Metodo filtra non implementato.")

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

    def filtra(self, queryset, termine):
        return filtra_queryset(queryset, termini_ricerca=termine,
                               campi_ricerca=['nome', 'cognome', 'codice_fiscale',])


class ElencoDettagliato(ElencoSemplice):
    """
    Un elenco che, esportato in excel, contiene tutti i dati
     anagrafici delle persone.
    """

    def excel_colonne(self):
        return super(ElencoDettagliato, self).excel_colonne() + (
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
        )


class ElencoSoci(ElencoDettagliato):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi soci
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                al_giorno=self.modulo_riempito.cleaned_data['al_giorno'],
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_SOCIO,
            ).via("appartenenze")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )

    def modulo(self):
        return ModuloElencoSoci

    def template(self):
        return 'us_elenchi_inc_soci.html'

    def excel_foglio(self, p):
        return p.sedi_attuali(al_giorno=self.modulo_riempito.cleaned_data['al_giorno'], membro__in=Appartenenza.MEMBRO_SOCIO).first().nome

    def excel_colonne(self):
        return super(ElencoSoci, self).excel_colonne() + (
            ("Ingresso in CRI", lambda p: p.ingresso())
        )

