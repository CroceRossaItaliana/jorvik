from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta
from django.utils import timezone
from django.db.models import Q, F
from django.utils.encoding import force_text

from anagrafica.models import (Persona, Appartenenza, Riserva, Sede,
                               Fototessera, ProvvedimentoDisciplinare,
                               Trasferimento, Dimissione, Estensione)
from attivita.models import Partecipazione
from base.utils import filtra_queryset, testo_euro, oggi
from curriculum.models import TitoloPersonale, Titolo
from .models import Tesseramento, Quota, Tesserino, ReportElenco
from .forms import (ModuloElencoSoci, ModuloElencoElettorato, ModuloElencoQuote)


class Elenco:
    """ Rappresenta un elenco semplice di persone. """

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
        columns = (
            ("Cognome", lambda p: p.cognome),
            ("Nome", lambda p: p.nome),
            ("Codice Fiscale", lambda p: p.codice_fiscale),
        )
        return super().excel_colonne() + columns

    def ordina(self, qs):
        return qs.order_by('cognome', 'nome', 'codice_fiscale', )

    def filtra(self, queryset, termine):
        return filtra_queryset(queryset, termini_ricerca=termine,
                               campi_ricerca=['nome', 'cognome', 'codice_fiscale', ])

    def template(self):
        return 'us_elenchi_inc_persone.html'


class ElencoVistaAnagrafica(ElencoVistaSemplice):
    """
    Un elenco che, esportato in excel, contiene tutti i dati
     anagrafici delle persone.
    """

    SHORT_NAME = 'ea'  # utilizzato in anagrafica.profile.menu.filter_per_role

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
            ("Indirizzo di domicilio", lambda p: p.domicilio_indirizzo),
            ("Comune di domicilio", lambda p: p.domicilio_comune),
            ("Provincia di domicilio", lambda p: p.domicilio_provincia),
            ("Stato di domicilio", lambda p: p.domicilio_stato),
            ("CAP di domicilio", lambda p: p.domicilio_cap),
            ("Email", lambda p: p.email),
            ("Numeri di telefono", lambda p: ", ".join([str(x) for x in p.numeri_telefono.all()])),
        )


class ElencoVistaSoci(ElencoVistaAnagrafica):
    SHORT_NAME = 'us'  # utilizzato in anagrafica.profile.menu.filter_per_role

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
            scelte = dict(Appartenenza._meta.get_field('membro').flatchoices)
            return force_text(scelte[p.appartenenza_tipo], strings_only=True)

        return super(ElencoVistaSoci, self).excel_colonne() + (
            ("Giovane", lambda p: "Si" if p.giovane else "No"),
            ("Ingresso in CRI", lambda p: p.ingresso().date()),
            ("Tipo Attuale", lambda p: _tipo_socio(p) if p.appartenenza_tipo else "N/A"),
            ("A partire dal", lambda p: p.appartenenza_inizio.date() if p.appartenenza_inizio else "N/A"),
        )


class ElencoVistaTesseriniRifiutati(ElencoVistaSoci):
    """
    Aggiunge all'elecno, esportato in excel, il motivo del rifiuto
     del tesserino e il tipo di rilascio.
    """

    def excel_colonne(self):
        return super(ElencoVistaTesseriniRifiutati, self).excel_colonne() + (
            ("Motivo rifiuto tesserino", lambda p: p.ultimo_tesserino.motivo_rifiutato),
            ("Tipo richiesta tesserino", lambda p: p.ultimo_tesserino.get_tipo_richiesta_display())
        )


class ElencoSociAlGiorno(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi soci """

    REPORT_TYPE = ReportElenco.SOCI_AL_GIORNO

    def risultati(self):
        qs_sedi = self.args[0]

        al_giorno = self.modulo_riempito.cleaned_data['al_giorno']

        return Persona.objects.filter(
            Appartenenza.query_attuale(
                al_giorno=al_giorno,
                sede__in=qs_sedi,
                membro__in=Appartenenza.MEMBRO_SOCIO,
            ).via("appartenenze")
        ).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede', 'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def modulo(self):
        return ModuloElencoSoci


class ElencoSostenitori(ElencoVistaAnagrafica):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.SOSTENITORI

    def template(self):
        return 'us_elenchi_inc_sostenitori.html'

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


class ElencoExSostenitori(ElencoVistaAnagrafica):
    REPORT_TYPE = ReportElenco.EX_SOSTENITORI

    def risultati(self):
        qs_sedi = self.args[0]

        sostenitori = Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro=Appartenenza.SOSTENITORE,
            ).via("appartenenze")
        ).values_list('pk', flat=True)
        ex = Persona.objects.filter(
            appartenenze__in=Appartenenza.objects.filter(
                sede__in=qs_sedi, membro=Appartenenza.SOSTENITORE,
                fine__isnull=False
            )
        ).exclude(pk__in=sostenitori)
        return ex.prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )


class ElencoVolontari(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori"""

    REPORT_TYPE = ReportElenco.VOLONTARI

    def modulo(self):
        from .forms import ModuloElencoVolontari
        return ModuloElencoVolontari

    def risultati(self):
        qs_sedi = self.args[0]

        modulo = self.modulo_riempito
        if modulo and modulo.cleaned_data['includi_estesi'] == modulo.SI:
            appartenenze = [Appartenenza.VOLONTARIO, Appartenenza.ESTESO]
        else:
            appartenenze = [Appartenenza.VOLONTARIO, ]

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
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.IV_E_CM

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


class ElencoIV(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.IV

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Q(iv=True),
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


class ElencoCM(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.CM

    def risultati(self):
        qs_sedi = self.args[0]

        return Persona.objects.filter(
            Q(cm=True),
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


class ElencoSenzaTurni(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.SENZA_TURNI

    def modulo(self):
        from .forms import ModuloSenzaTurni
        return ModuloSenzaTurni

    def risultati(self):
        qs_sedi = self.args[0]

        modulo = self.modulo_riempito
        attivi = Partecipazione.objects.filter(
            turno__fine__gte=modulo.cleaned_data['inizio'], turno__inizio__lte=modulo.cleaned_data['fine'],
            turno__attivita__sede__in=qs_sedi,
            confermata=True,
        ).values_list('persona_id', flat=True)
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_ATTIVITA,
            ).via("appartenenze")
        ).exclude(pk__in=attivi).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoEstesi(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.ESTESI

    def modulo(self):
        from .forms import ModuloElencoEstesi
        return ModuloElencoEstesi

    def risultati(self):
        qs_sedi = self.args[0]

        from django.db.models import BooleanField, Value
        if self.modulo_riempito.cleaned_data['estesi'] == self.modulo_riempito.ESTESI_INGRESSO:
            # Estesi in ingresso
            risultati = Persona.objects.filter(
                Appartenenza.query_attuale(
                    sede__in=qs_sedi, membro=Appartenenza.ESTESO,
                ).via("appartenenze")
            ).annotate(is_ingresso=Value(value=True, output_field=BooleanField()))

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
            ).annotate(is_ingresso=Value(value=False, output_field=BooleanField()))

        return risultati.annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def excel_colonne(self):

        def _comitato(p):
            if not p.is_ingresso:
                return Estensione.objects.filter(persona=p.pk, ritirata=False).order_by(
                    'creazione').first().destinazione
            else:
                return p.appartenenze_attuali().filter(fine=None).first().sede

        return super(ElencoEstesi, self).excel_colonne() + (
            ('Data inizio estensione', lambda p: Estensione.objects.filter(persona=p.pk, ritirata=False).order_by(
                'creazione').first().protocollo_data),
            ('Comitato di estensione', lambda p: _comitato(p)),
        )


class ElencoVolontariGiovani(ElencoVolontari):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.VOLONTARI_GIOVANI

    def risultati(self):
        oggi = date.today()
        nascita_minima = date(oggi.year - Persona.ETA_GIOVANE, oggi.month, oggi.day)
        return super(ElencoVolontariGiovani, self).risultati().filter(
            data_nascita__gt=nascita_minima
        ).distinct('cognome', 'nome', 'codice_fiscale')


class ElencoDimessi(ElencoVistaAnagrafica):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi """

    REPORT_TYPE = ReportElenco.DIMESSI

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

    def excel_colonne(self):
        def _data(p):
            dim = Dimissione.objects.filter(persona=p.pk).order_by('ultima_modifica').first()
            return dim.creazione if dim else ''

        def _motivo(p):
            dim = Dimissione.objects.filter(persona=p.pk).order_by('ultima_modifica').first()
            motivi = dict(Dimissione.MOTIVI)
            return motivi[dim.motivo] if dim else ''

        return super(ElencoDimessi, self).excel_colonne() + (
            ('Data dimissioni', lambda p: _data(p)),
            ('Motivazioni', lambda p: _motivo(p))
        )


class ElencoTrasferiti(ElencoVistaAnagrafica):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi """

    REPORT_TYPE = ReportElenco.TRASFERITI

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            appartenenze__sede__in=qs_sedi,
            appartenenze__terminazione__in=[Appartenenza.TRASFERIMENTO, ],

        ).exclude(  # Escludi tutti i membri attuali delle mie sedi (es. trasf. interni)
            pk__in=Persona.objects.filter(
                Appartenenza.query_attuale(
                    sede__in=qs_sedi,
                    terminazione__in=[Appartenenza.TRASFERIMENTO, ],
                ).via("appartenenze")
            ).values_list('id', flat=True)
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def excel_colonne(self):
        def _data(p):
            d = Trasferimento.objects.filter(persona=p.id, ritirata=False).order_by('-id')
            return d.first().protocollo_data if d else ''

        def _motivo(p):
            d = Trasferimento.objects.filter(persona=p.id, ritirata=False).order_by('-id')
            return d.first().motivo if d else ''

        def _destinazione(p):
            d = Trasferimento.objects.filter(persona=p.id, ritirata=False).order_by('-id')
            return d.first().destinazione if d else ''

        return super(ElencoTrasferiti, self).excel_colonne() + (
            ('Data del trasferimento', lambda p: _data(p)),
            ('Comitato di destinazione', lambda p: _destinazione(p)),
            ('Motivazione', lambda p: _motivo(p)),
        )


class ElencoDipendenti(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.DIPENDENTI

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
    """ args: QuerySet<Sede> Sedi per le quali compilare gli elenchi quote associative """
    NAME = 'Quote'

    def modulo(self):
        return ModuloElencoQuote

    def risultati(self):
        qs_sedi = self.args[0]
        modulo = self.modulo_riempito

        membri = modulo.cleaned_data['membri']
        attivi = membri == modulo.MEMBRI_VOLONTARI
        ordinari = membri == modulo.MEMBRI_ORDINARI

        anno = modulo.cleaned_data['anno']

        try:
            tesseramento = Tesseramento.objects.get(anno=anno)

        except Tesseramento.DoesNotExist:  # Errore tesseramento anno non esistente
            raise ValueError("Anno di tesseramento non valido o gestito da Gaia.")

        # Dobbiamo ridurre il set a tutti i volontari che sono, al giorno attuale, appartenenti a questa sede
        # Nel caso di un anno passato, generiamo l'elenco al 31 dicembre. Nel caso dell'anno in corso,
        # generiamo l'elenco al giorno attuale. Questo e' equivalente a:
        #  giorno = min(31/dicembre/<anno selezionato>, oggi)
        giorno_appartenenza = min(date(day=31, month=12, year=anno), oggi())

        if modulo.cleaned_data['tipo'] == modulo.VERSATE:
            origine = tesseramento.paganti(attivi=attivi, ordinari=ordinari)  # Persone con quote pagate

        else:
            origine = tesseramento.non_paganti(attivi=attivi, ordinari=ordinari)  # Persone con quote NON pagate

        # Ora filtra per Sede
        q = Appartenenza.query_attuale(
            al_giorno=giorno_appartenenza,
            membro=Appartenenza.VOLONTARIO
        ).filter(sede__in=qs_sedi).defer('membro', 'inizio', 'sede')

        return origine.filter(appartenenze__in=q).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related('quote').distinct('cognome', 'nome', 'codice_fiscale')

    def excel_colonne(self):
        anno = self.modulo_riempito.cleaned_data['anno']
        return super(ElencoQuote, self).excel_colonne() + (
            ("Importo quota",
             lambda p: ', '.join([testo_euro(q.importo_totale) for q in p.quote_anno(anno, stato=Quota.REGISTRATA)])),
            ("Data versamento", lambda p: ', '.join(
                [q.data_versamento.strftime('%d/%m/%y') for q in p.quote_anno(anno, stato=Quota.REGISTRATA)])),
            ("Registrata da", lambda p: ', '.join(
                [q.registrato_da.nome_completo for q in p.quote_anno(anno, stato=Quota.REGISTRATA) if q.registrato_da])
             ),
        )

    def template(self):
        modulo = self.modulo_riempito
        return 'us_elenchi_inc_quote.html'


class ElencoOrdinari(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.SOCI_ORDINARI

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
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi in riserva """

    REPORT_TYPE = ReportElenco.VOLONTARI_IN_RISERVA

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Riserva.query_attuale(
                Riserva.con_esito_ok().q,
                Appartenenza.query_attuale(
                    sede__in=qs_sedi
                ).via("appartenenza"),
            ).via("riserve")
        ).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def excel_colonne(self):
        def riserva(p, attr):
            query = Riserva.objects.filter(
                Q(fine__gte=timezone.now()) | Q(fine__isnull=True),
                persona=p.id)
            if query:
                return getattr(query.last(), attr)
            return ''

        return super().excel_colonne() + (
            ("Data inizio", lambda p: riserva(p, 'inizio')),
            ("Data fine", lambda p: riserva(p, 'fine')),
            ("Motivazioni", lambda p: riserva(p, 'motivo'))
        )


class ElencoElettoratoAlGiorno(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori """

    REPORT_TYPE = ReportElenco.ELETTORATO

    def risultati(self):
        from datetime import datetime

        qs_sedi = self.args[0]
        form = self.modulo_riempito
        cd = form.cleaned_data

        oggi = cd['al_giorno']  # date
        elettorato = cd['elettorato']

        # Impostazione Anzianità
        oggi = datetime.combine(oggi, datetime.min.time())  # date -> datetime
        delta_months = oggi - relativedelta(months=Appartenenza.MEMBRO_ANZIANITA_MESI)
        anzianita_minima = delta_months.replace(hour=23, minute=59, second=59)

        aggiuntivi = {
            # Anzianita' minima 
            "pk__in": Persona.objects.filter(
                Appartenenza.con_esito_ok(
                    membro__in=[Appartenenza.VOLONTARIO, ],
                    inizio__lte=anzianita_minima,
                    terminazione__isnull=True,
                ).via("appartenenze")
            ).only("id")
        }

        # Impostazione età minima
        ETA_MINIMA_ANNI = 18 if elettorato == ModuloElencoElettorato.ELETTORATO_PASSIVO else 14
        nascita_minima = date(oggi.year - ETA_MINIMA_ANNI, oggi.month, oggi.day)

        # Update criteri query
        aggiuntivi.update({
            # Registrazione versamento della quota associativa annuale (da commentare)
            # 'quota__stato': Quota.REGISTRATA,
            # 'quota__tipo': Quota.QUOTA_SOCIO,

            "data_nascita__lte": nascita_minima,  # Età minima
        })

        # Cerca dipendenti da escludere
        dipendenti = Persona.objects.filter(
            Q(Appartenenza.query_attuale(
                membro=Appartenenza.DIPENDENTE,
                sede__in=qs_sedi,
                al_giorno=oggi,
            ).via("appartenenze")))

        # print("dipendenti", dipendenti.values_list('pk', flat=True) )

        # Query finale
        persone = Persona.objects.filter(Appartenenza.query_attuale(
            membro=Appartenenza.VOLONTARIO,
            sede__in=qs_sedi,
            al_giorno=oggi,
        ).via("appartenenze"), Q(**aggiuntivi))

        r = persone.exclude(
            # Escludi quelli con provvedimento di sospensione non terminato
            pk__in=ProvvedimentoDisciplinare.objects.filter(
                Q(fine__lte=oggi) | Q(fine__isnull=True),
                inizio__gte=oggi - relativedelta(months=24),
                tipo__in=[ProvvedimentoDisciplinare.SOSPENSIONE,
                          ProvvedimentoDisciplinare.ESPULSIONE,
                          ProvvedimentoDisciplinare.RADIAZIONE, ]
            ).values_list('persona__id', flat=True)

        ).exclude(
            pk__in=dipendenti.values_list('pk', flat=True)
        )

        # Escludi nelle liste elettorali di dove è volontario, essendo dipendente,
        # anche se in un altro comitato, non DEVE essere nella lista ne attiva e ne passiva
        qs_sedi_pk_list = qs_sedi if isinstance(qs_sedi, list) else qs_sedi.values_list('pk', flat=True)

        return r.exclude(
            pk__in=Appartenenza.query_attuale(
                membro=Appartenenza.DIPENDENTE,
                al_giorno=oggi,
                sede__pk__in=set(qs_sedi_pk_list) ^
                             set(Persona.objects.filter(pk__in=r.values_list('pk', flat=True)).values_list(
                                 'appartenenze__sede__pk', flat=True)),
            ).values_list('persona__pk', flat=True)
        ).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede', 'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def modulo(self):
        return ModuloElencoElettorato


class ElencoPerTitoli(ElencoVistaAnagrafica):
    REPORT_TYPE = ReportElenco.TITOLI

    def risultati(self):
        qs_sedi = self.args[0]

        cd = self.modulo_riempito.cleaned_data
        metodo = cd['metodo']
        titoli = cd['titoli']
        skills = cd['skill']

        base = Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_SOCIO,
            ).via("appartenenze")
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        )

        if metodo == self.modulo_riempito.METODO_OR:
            # Almeno un titolo

            if skills:
                base = base.filter(titoli_personali__in=TitoloPersonale.con_esito_ok().filter(
                    titolo__in=titoli, skills__in=skills
                )).distinct('cognome', 'nome', 'codice_fiscale')
            else:
                base = base.filter(titoli_personali__in=TitoloPersonale.con_esito_ok().filter(
                    titolo__in=titoli
                )).distinct('cognome', 'nome', 'codice_fiscale')

            return base
        else:
            # Tutti i titoli
            base = base.filter(titoli_personali__in=TitoloPersonale.con_esito_ok())
            for titolo in titoli:
                base = base.filter(titoli_personali__titolo=titolo)

            if skills:
                for skill in skills:
                    base = base.filter(titoli_personali__skills__in=[skill])

            return base.distinct('cognome', 'nome', 'codice_fiscale')

    def modulo(self):
        from .forms import ModuloElencoPerTitoli
        return ModuloElencoPerTitoli

    def excel_colonne(self):
        def titoli(p):
            return '\n'.join(
                [
                    "{} - {} - {}".format(
                        titolo.titolo.nome,
                        titolo.data_ottenimento if titolo.data_ottenimento else '',
                        titolo.data_scadenza if titolo.data_scadenza else ''
                    ) for titolo in p.titoli_personali_confermati()
                ]
            )

        return super().excel_colonne() + (
            ("Titoli - Data ottenimento - Data scadenza", lambda p: titoli(p)),
            ("Comitato di appartenenza", lambda p: p.sede_riferimento()),
        )


class ElencoPerTitoliCorso(ElencoPerTitoli):
    def risultati(self):
        cd = self.modulo_riempito.cleaned_data
        self.kwargs['cleaned_data'] = cd

        # Mostra persone con titoli scaduti/non scaduti
        results = super().risultati()
        return results.filter(titoli_personali__in=TitoloPersonale.con_esito_ok())

    def modulo(self):
        from .forms import ModuloElencoPerTitoliCorso
        return ModuloElencoPerTitoliCorso

    def template(self):
        return 'formazione_albo_inc_elenchi_persone_titoli.html'


class ElencoTesseriniRichiesti(ElencoVistaSoci):
    REPORT_TYPE = ReportElenco.TESSERINI_RICHIESTI

    def risultati(self):
        qs_sedi = self.args[0]
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),
            tesserini__stato_richiesta__in=(Tesserino.ACCETTATO, Tesserino.RICHIESTO, Tesserino.DUPLICATO),
        ).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
            tesserino_pk=F('tesserini__pk'),
            tesserino_codice=F('tesserini__codice'),
            tesserino_tipo_richiesta=F('tesserini__tipo_richiesta'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')

    def template(self):
        return "us_elenchi_inc_tesserini_richiesti.html"


class ElencoTesseriniDaRichiedere(ElencoTesseriniRichiesti):
    REPORT_TYPE = ReportElenco.TESSERINI_DA_RICHIEDERE

    def risultati(self):
        qs_sedi = self.args[0]
        tesserini_richiesti = super(ElencoTesseriniDaRichiedere, self).risultati()
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),

            # Con fototessera confermata
            Q(Fototessera.con_esito_ok().via("fototessere")),

            # Escludi tesserini rifiutati
            ~Q(tesserini__stato_richiesta=Tesserino.RIFIUTATO),

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
    REPORT_TYPE = ReportElenco.TESSERINI_SENZA_FOTOTESSERA

    def risultati(self):
        qs_sedi = self.args[0]
        tesserini_da_richiedere = super(ElencoTesseriniSenzaFototessera, self).risultati()
        tesserini_richiesti = super(ElencoTesseriniDaRichiedere, self).risultati()
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),

            ~Q(Fototessera.con_esito_ok().via("fototessere"))

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


class ElencoTesseriniRifiutati(ElencoVistaTesseriniRifiutati, ElencoTesseriniRichiesti):
    REPORT_TYPE = ReportElenco.TESSERINI_RIFIUTATI

    def risultati(self):
        qs_sedi = self.args[0]
        tesserini_richiesti = super(ElencoTesseriniRifiutati, self).risultati()
        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro__in=Appartenenza.MEMBRO_TESSERINO,
            ).via("appartenenze"),

            # Escludi tesserini non rifiutati
            Q(tesserini__stato_richiesta=Tesserino.RIFIUTATO),

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
        return "us_elenchi_inc_tesserini_rifiutati.html"


class ElencoServizioCivile(ElencoVistaSoci):
    """ args: QuerySet<Sede>, Sedi per le quali compilare gli elenchi sostenitori"""

    REPORT_TYPE = ReportElenco.SERVIZIO_CIVILE

    def risultati(self):
        qs_sedi = self.args[0]

        return Persona.objects.filter(
            Appartenenza.query_attuale(
                sede__in=qs_sedi, membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE,
            ).via("appartenenze")
        ).annotate(
            appartenenza_tipo=F('appartenenze__membro'),
            appartenenza_inizio=F('appartenenze__inizio'),
            appartenenza_sede=F('appartenenze__sede'),
        ).prefetch_related(
            'appartenenze', 'appartenenze__sede',
            'utenza', 'numeri_telefono'
        ).distinct('cognome', 'nome', 'codice_fiscale')
