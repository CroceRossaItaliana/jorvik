from django.contrib.admin import ModelAdmin
from django.db.models import Q, F
from django.utils.encoding import force_text

from anagrafica.models import Persona, Appartenenza, Riserva, Sede, Fototessera
from base.utils import filtra_queryset, testo_euro
from curriculum.models import TitoloPersonale
from ufficio_soci.forms import ModuloElencoSoci, ModuloElencoElettorato, ModuloElencoQuote, ModuloElencoPerTitoli
from datetime import date, datetime
from django.utils.timezone import now

from ufficio_soci.models import Tesseramento, Quota, Tesserino


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



class ElencoVistaSemplice(Elenco):

    def excel_colonne(self):
        return super(ElencoVistaSemplice, self).excel_colonne() + (
            ("Cognome", lambda p: p.cognome),
            ("Nome", lambda p: p.nome),
            ("Codice Fiscale", lambda p: p.codice_fiscale),
        )

    def ordina(self, qs):
        return qs.order_by('cognome', 'nome', 'codice_fiscale',)

    def filtra(self, queryset, termine):
        return filtra_queryset(queryset, termini_ricerca=termine,
                               campi_ricerca=['nome', 'cognome', 'codice_fiscale',])

    def template(self):
        return 'us_elenchi_inc_persone.html'


class ElencoVistaAnagrafica(ElencoVistaSemplice):
    """
    Un elenco che, esportato in excel, contiene tutti i dati
     anagrafici delle persone.
    """

    def excel_colonne(self):
        return super(ElencoVistaAnagrafica, self).excel_colonne() + (
            ("Data di Nascita", lambda p: p.data_nascita),
            ("Luogo di Nascita", lambda p: p.comune_nascita),
            ("Provincia di Nascita", lambda p: p.provincia_nascita),
            ("Stato di Nascita", lambda p: p.stato_nascita),
            ("Indirizzo di residenza", lambda p: p.indirizzo_residenza),
            ("Comune di residenza", lambda p: p.comune_residenza),
            ("CAP di residenza", lambda p: p.cap_residenza),
            ("Provincia di residenza", lambda p: p.provincia_residenza),
            ("Stato di residenza", lambda p: p.stato_residenza),
            ("Email", lambda p: p.email),
            ("Numeri di telefono", lambda p: ", ".join([str(x) for x in p.numeri_telefono.all()])),
        )


class ElencoVistaSoci(ElencoVistaAnagrafica):

    def template(self):
        return 'us_elenchi_inc_soci.html'

    def excel_foglio(self, p):
        if hasattr(p, 'appartenenza_sede'):
            sede = Sede.objects.get(pk=p.appartenenza_sede)

        elif self.modulo_riempito and 'al_giorno' in self.modulo_riempito.cleaned_data \
                and self.modulo_riempito.cleaned_data['al_giorno']:
            sede = p.sede_riferimento(al_giorno=self.modulo_riempito.cleaned_data['al_giorno'])
        else:
            sede = p.sede_riferimento()

        return sede.nome_completo if sede else 'Altro'

    def excel_colonne(self):

        def _tipo_socio(p):
            scelte = dict(Appartenenza._meta.get_field_by_name('membro')[0].flatchoices)
            return force_text(scelte[p.appartenenza_tipo], strings_only=True)

        return super(ElencoVistaSoci, self).excel_colonne() + (
            ("Giovane", lambda p: "Si" if p.giovane else "No"),
            ("Ingresso in CRI", lambda p: p.ingresso().date()),
            ("Tipo Attuale", lambda p: _tipo_socio(p) if p.appartenenza_tipo else "N/A"),
            ("A partire dal", lambda p: p.appartenenza_inizio.date() if p.appartenenza_inizio else "N/A")
        )


class ElencoSociAlGiorno(ElencoVistaSoci):
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
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def modulo(self):
        return ModuloElencoSoci


class ElencoSostenitori(ElencoVistaAnagrafica):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro=Appartenenza.SOSTENITORE,
            ).via("appartenenze")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )


class ElencoVolontari(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def modulo(self):
        from .forms import ModuloElencoVolontari
        return ModuloElencoVolontari

    def risultati(self):
        qs_sedi = self.args[0]

        modulo = self.modulo_riempito
        if modulo.cleaned_data['includi_estesi'] == modulo.SI:
            appartenenze = [Appartenenza.VOLONTARIO, Appartenenza.ESTESO]
        else:
            appartenenze = [Appartenenza.VOLONTARIO,]

        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=appartenenze,
            ).via("appartenenze")
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoIVCM(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def modulo(self):
        from .forms import ModuloElencoIVCM
        return ModuloElencoIVCM

    def risultati(self):
        qs_sedi = self.args[0]

        modulo = self.modulo_riempito
        query = Q()
        if modulo.IV == modulo.cleaned_data['includi']:
            query &= Q(iv=True)
        if modulo.CM == modulo.cleaned_data['includi']:
            query &= Q(cm=True)
        return Persona.objects.filter(
            query,
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_DIRETTO,
            ).via("appartenenze")
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoEstesi(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def modulo(self):
        from .forms import ModuloElencoEstesi
        return ModuloElencoEstesi

    def risultati(self):
        qs_sedi = self.args[0]

        if self.modulo_riempito.cleaned_data['estesi'] == self.modulo_riempito.ESTESI_INGRESSO:
            # Estesi in ingresso
            risultati = Persona.objects.filter(
                Appartenenza.query_attuale(
                    sede__in=qs_sedi, membro=Appartenenza.ESTESO,
                ).via("appartenenze")
            )

        else:
            # Estesi in uscita
            estesi_da_qualche_parte = Persona.objects.filter(
                Appartenenza.query_attuale(
                    membro=Appartenenza.ESTESO
                ).via("appartenenze")
            ).values_list('pk', flat=True)

            volontari_da_me = Persona.objects.filter(
                Appartenenza.query_attuale(
                    sede__in=qs_sedi, membro=Appartenenza.VOLONTARIO,
                ).via("appartenenze")
            ).values_list('pk', flat=True)

            risultati = Persona.objects.filter(
                pk__in=volontari_da_me
            ).filter(
                pk__in=estesi_da_qualche_parte
            )

        return risultati.annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoVolontariGiovani(ElencoVolontari):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def risultati(self):
        oggi = date.today()
        nascita_minima = date(oggi.year - Persona.ETA_GIOVANE, oggi.month, oggi.day)
        return super(ElencoVolontariGiovani, self).risultati().filter(
            data_nascita__gt=nascita_minima
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoDimessi(ElencoVistaAnagrafica):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            ~Appartenenza.query_attuale(
                sede__in=qs_sedi,
            ).via("appartenenze"),
            appartenenze__sede__in=qs_sedi,
            appartenenze__terminazione__in=[Appartenenza.DIMISSIONE, Appartenenza.ESPULSIONE],
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoTrasferiti(ElencoVistaAnagrafica):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            appartenenze__sede__in=qs_sedi,
            appartenenze__terminazione__in=[Appartenenza.TRASFERIMENTO,],

        ).exclude(  # Escludi tutti i membri attuali delle mie sedi (es. trasf. interni)
            pk__in=Persona.objects.filter(
                Appartenenza.query_attuale(
                    sede__in=qs_sedi
                ).via("appartenenze")
            ).values_list('id', flat=True)

        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoDipendenti(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro=Appartenenza.DIPENDENTE,
            ).via("appartenenze")
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoQuote(ElencoVistaSoci):
    """
    args: QuerySet<Sede> Sedi per le quali compilare gli elenchi quote associative
    """
    def modulo(self):
        return ModuloElencoQuote

    def risultati(self):
        qs_sedi = self.args[0]
        modulo = self.modulo_riempito

        membri = modulo.cleaned_data['membri']
        attivi = membri == modulo.MEMBRI_VOLONTARI
        ordinari = membri == modulo.MEMBRI_ORDINARI

        try:
            tesseramento = Tesseramento.objects.get(anno=modulo.cleaned_data.get('anno'))

        except Tesseramento.DoesNotExist:  # Errore tesseramento anno non esistente
            raise ValueError("Anno di tesseramento non valido o gestito da Gaia.")

        if modulo.cleaned_data['tipo'] == modulo.VERSATE:
            origine = tesseramento.paganti(attivi=attivi, ordinari=ordinari)  # Persone con quote pagate

        else:
            origine = tesseramento.non_paganti(attivi=attivi, ordinari=ordinari)  # Persone con quote NON pagate

        # Ora filtra per Sede
        return origine.filter(
            appartenenze__sede__in=qs_sedi,
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related('quote').distinct('cognome', 'nome', 'codice_fiscale')

    def excel_colonne(self):
        anno = self.modulo_riempito.cleaned_data['anno']
        return super(ElencoQuote, self).excel_colonne() + (
            ("Importo quota", lambda p: ', '.join([testo_euro(q.importo_totale) for q in p.quote_anno(anno, stato=Quota.REGISTRATA)])),
            ("Data versamento", lambda p: ', '.join([q.data_versamento.strftime('%d/%m/%y') for q in p.quote_anno(anno, stato=Quota.REGISTRATA)])),
            ("Registrata da", lambda p: ', '.join([q.registrato_da.nome_completo for q in p.quote_anno(anno, stato=Quota.REGISTRATA)])),
        )

    def template(self):
        modulo = self.modulo_riempito
        return 'us_elenchi_inc_quote.html'



class ElencoOrdinari(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro=Appartenenza.ORDINARIO,
            ).via("appartenenze")
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoInRiserva(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi in riserva
    """

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Riserva.query_attuale(
                Riserva.con_esito_ok().q,
                Appartenenza.query_attuale(
                    sede__in=qs_sedi
                ).via("appartenenza")
            ).via("riserve")
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoElettoratoAlGiorno(ElencoVistaSoci):
    """
    args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi soci
    """

    def risultati(self):
        qs_sedi = self.args[0]

        oggi = self.modulo_riempito.cleaned_data['al_giorno']
        nascita_minima = date(oggi.year - 18, oggi.month, oggi.day)
        anzianita_minima = datetime(oggi.year - Appartenenza.MEMBRO_ANZIANITA_ANNI, oggi.month, oggi.day, 23, 59, 59)

        aggiuntivi = {
            # Anzianita' minima
            "pk__in": Persona.objects.filter(
                Appartenenza.con_esito_ok(
                    membro__in=Appartenenza.MEMBRO_ANZIANITA,
                    inizio__lte=anzianita_minima
                ).via("appartenenze")
            ).only("id")
        }
        if self.modulo_riempito.cleaned_data['elettorato'] == ModuloElencoElettorato.ELETTORATO_PASSIVO:
            # Elettorato passivo,
            aggiuntivi.update({
                # Eta' minima
                "data_nascita__lte": nascita_minima,
            })

        r = Persona.objects.filter(
            Appartenenza.query_attuale(
                al_giorno=oggi,
                sede__in=qs_sedi, membro=Appartenenza.VOLONTARIO,
            ).via("appartenenze"),
            Q(**aggiuntivi),

        ).exclude(  # Escludi quelli con dimissione negli anni di anzianita'
            appartenenze__terminazione__in=[Appartenenza.DIMISSIONE, Appartenenza.ESPULSIONE],
            appartenenze__fine__gte=anzianita_minima,

        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')
        return r

    def modulo(self):
        return ModuloElencoElettorato


class ElencoPerTitoli(ElencoVistaAnagrafica):

    def risultati(self):
        qs_sedi = self.args[0]

        metodo = self.modulo_riempito.cleaned_data['metodo']
        titoli = self.modulo_riempito.cleaned_data['titoli']

        base = Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_SOCIO,
            ).via("appartenenze")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )

        if metodo == self.modulo_riempito.METODO_OR:  # Almeno un titolo

            return base.filter(titoli_personali__in=TitoloPersonale.con_esito_ok().filter(
                    titolo__in=titoli,
            )).distinct('cognome', 'nome', 'codice_fiscale')

        else:  # Tutti i titoli

            base = base.filter(
                titoli_personali__in=TitoloPersonale.con_esito_ok()
            )

            for titolo in titoli:
                base = base.filter(
                    titoli_personali__titolo=titolo
                )

            return base.distinct('cognome', 'nome', 'codice_fiscale')

    def modulo(self):
        return ModuloElencoPerTitoli


class ElencoTesseriniRichiesti(ElencoVistaSoci):

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),
            tesserini__stato_richiesta__in=(Tesserino.ACCETTATO, Tesserino.RICHIESTO, Tesserino.DUPLICATO),
            tesserini__valido=True
        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
                tesserino_codice=F('tesserini__codice'),
                tesserino_tipo_richiesta=F('tesserini__tipo_richiesta'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def template(self):
        return "us_elenchi_inc_tesserini_richiesti.html"


class ElencoTesseriniDaRichiedere(ElencoTesseriniRichiesti):

    def risultati(self):
        qs_sedi = self.args[0]
        tesserini_richiesti = super(ElencoTesseriniDaRichiedere, self).risultati()
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),

            # Con fototessera confermata
            Fototessera.con_esito_ok().via("fototessere"),

        ).exclude(  # Escludi quelli richiesti da genitore
            pk__in=tesserini_richiesti.values_list('id', flat=True)

        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def template(self):
        return "us_elenchi_inc_tesserini_da_richiedere.html"


class ElencoTesseriniSenzaFototessera(ElencoTesseriniDaRichiedere):

    def risultati(self):
        qs_sedi = self.args[0]
        tesserini_da_richiedere = super(ElencoTesseriniSenzaFototessera, self).risultati()
        tesserini_richiesti = super(ElencoTesseriniDaRichiedere, self).risultati()
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),

        ).exclude(  # Escludi quelli che posso richiedere
            pk__in=tesserini_da_richiedere.values_list('id', flat=True)
        ).exclude(  # Escludi quelli gia richiesti
            pk__in=tesserini_richiesti.values_list('id', flat=True),

        ).annotate(
                appartenenza_tipo=F('appartenenze__membro'),
                appartenenza_inizio=F('appartenenze__inizio'),
                appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def template(self):
        return "us_elenchi_inc_tesserini_senza_fototessera.html"