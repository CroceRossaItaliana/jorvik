import datetime
import operator

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from anagrafica.costanti import LOCALE, REGIONALE
from anagrafica.models import Appartenenza, Delega, Sede
from anagrafica.permessi.applicazioni import PRESIDENTE, UFFICIO_SOCI, DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, REFERENTE, RESPONSABILE_AUTOPARCO, RESPONSABILE_FORMAZIONE
from attivita.models import Attivita, Partecipazione



# Costanti

LIMITE_ETA = 35
LIMITE_ANNI_ATTIVITA = 1

# Utils

def _appartenenze_attive(queryset):
    return queryset.filter(
        appartenenze__in=Appartenenza.query_attuale().values_list('pk', flat='True')
    )


def _deleghe_attive(queryset):
    return queryset.filter(
        delega__in=Delega.query_attuale().values_list('pk', flat='True')
    )


def _calcola_eta(queryset, meno=True):
    controllo = operator.lt if meno else operator.ge

    persone_filtrate = []
    for persona in queryset:
        if controllo(persona.eta, LIMITE_ETA):
            persone_filtrate.append(persona.pk)
    return persone_filtrate


def _calcola_anni_attivita(queryset, meno=True):
    controllo = operator.lt if meno else operator.gt

    persone_filtrate = []
    for persona in queryset:
        oggi = datetime.date.today()
        storico = Partecipazione.con_esito_ok().filter(persona=persona, stato=Partecipazione.RICHIESTA)\
            .order_by('-turno__inizio')

        anni_attivita = storico.dates('turno__inizio', 'year', order='DESC').count()

        if controllo(anni_attivita, LIMITE_ANNI_ATTIVITA):
            persone_filtrate.append(persona.pk)
    return persone_filtrate


# TODO: Aggiungere test per i filtri che utilizzano questa funzione
def _referenti_attivita(queryset, obiettivo=0):
    qs = queryset.filter(delega__tipo=REFERENTE)
    if obiettivo > 0:
        attivita_area = Attivita.objects.filter(area__obiettivo=obiettivo)
        referenti = attivita_area.referenti_attuali()
        referenti = referenti.value_list('pk', flat=True)
        qs = qs.filter(pk__in=referenti)
    return qs


def _presidenze_comitati(queryset, estensione=LOCALE):
    sedi = []
    sedi = Sede.objects.filter(tipo=Sede.COMITATO, estensione=estensione).values_list('id', flat=True)
    return queryset.filter(delega__oggetto_tipo=ContentType.objects.get_for_model(Sede), delega__oggetto_id__in=sedi.values_list('id', flat=True))


# Filtri

def volontari(queryset):
    tutti_volontari = queryset.filter(appartenenze__membro=Appartenenza.VOLONTARIO)
    return _appartenenze_attive(tutti_volontari)


def volontari_meno_un_anno(queryset):
    tutti_volontari = volontari(queryset).filter()
    volontari_filtrati = _calcola_anni_attivita(queryset)
    return tutti_volontari.filter(pk__in=volontari_filtrati)


def volontari_piu_un_anno(queryset):
    tutti_volontari = volontari(queryset).filter()
    volontari_filtrati = _calcola_anni_attivita(queryset, meno=False)
    return tutti_volontari.filter(pk__in=volontari_filtrati)


def volontari_meno_35_anni(queryset):
    tutti_volontari = volontari(queryset)
    volontari_filtrati = _calcola_eta(tutti_volontari)
    return tutti_volontari.filter(pk__in=volontari_filtrati)


def volontari_maggiore_o_uguale_35_anni(queryset):
    tutti_volontari = volontari(queryset)
    volontari_filtrati = volontari_filtrati = _calcola_eta(tutti_volontari, meno=False)
    return tutti_volontari.filter(pk__in=volontari_filtrati)


def sostenitori_cri(queryset):
    qs = queryset.filter(appartenenze__membro=Appartenenza.SOSTENITORE)
    return _appartenenze_attive(qs)


def aspiranti_volontari_iscritti_ad_un_corso(queryset):
    qs = queryset.filter(
        aspirante__isnull=False,
    )
    aspiranti_filtrati = []
    for persona in qs:
        if persona.partecipazione_corso_base():
            aspiranti_filtrati.append(persona.pk)
    qs = qs.filter(pk__in=aspiranti_filtrati)
    return qs


def tutti_i_presidenti(queryset):
    qs = queryset.filter(delega__tipo=PRESIDENTE)
    return _deleghe_attive(qs)


def presidenti_comitati_locali(queryset):
    return _presidenze_comitati(tutti_i_presidenti(queryset))


def presidenti_comitati_regionali(queryset):
    return _presidenze_comitati(tutti_i_presidenti(queryset), REGIONALE)


def delegati_US(queryset):
    qs = queryset.filter(delega__tipo=UFFICIO_SOCI)
    return _deleghe_attive(qs)


def delegati_Obiettivo_I(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_1)
    return _deleghe_attive(qs)


def delegati_Obiettivo_II(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_2)
    return _deleghe_attive(qs)


def delegati_Obiettivo_III(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_3)
    return _deleghe_attive(qs)


def delegati_Obiettivo_IV(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_4)
    return _deleghe_attive(qs)


def delegati_Obiettivo_V(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_5)
    return _deleghe_attive(qs)


def delegati_Obiettivo_VI(queryset):
    qs = queryset.filter(delega__tipo=DELEGATO_OBIETTIVO_6)
    return _deleghe_attive(qs)


def referenti_attivita_area_I(queryset):
    return _referenti_attivita(queryset, 1)


def referenti_attivita_area_II(queryset):
    return _referenti_attivita(queryset, 2)


def referenti_attivita_area_III(queryset):
    return _referenti_attivita(queryset, 3)


def referenti_attivita_area_IV(queryset):
    return _referenti_attivita(queryset, 4)


def referenti_attivita_area_V(queryset):
    return _referenti_attivita(queryset, 5)


def referenti_attivita_area_VI(queryset):
    return _referenti_attivita(queryset, 6)


def delegati_autoparco(queryset):
    qs = queryset.filter(delega__tipo=RESPONSABILE_AUTOPARCO)
    return _deleghe_attive(qs)


def delegati_formazione(queryset):
    qs = queryset.filter(delega__tipo=RESPONSABILE_FORMAZIONE)
    return _deleghe_attive(qs)


# TODO: fare dei test e specificare con precisione come filtrare sui titoli
def volontari_con_titolo(queryset):
    return volontari(queryset).filter(titoli_personali__confermata=True)


NOMI_SEGMENTI = (
    ('A', 'Tutti gli utenti di Gaia'),
    ('B', 'Volontari'),
    ('C', 'Volontari da meno di un anno'),
    ('D', 'Volontari da più di un anno'),
    ('E', 'Volontari con meno di 35 anni'),
    ('F', 'Volontari con 35 anni o più'),
    ('G', 'Sostenitori CRI'),
    ('H', 'Aspiranti volontari iscritti a un corso'),
    ('I', 'Tutti i Presidenti'),
    ('J', 'Presidenti di Comitati Locali'),
    ('K', 'Presidenti di Comitati Regionali'),
    ('L', 'Delegati US'),
    ('M', 'Delegati Obiettivo I'),
    ('N', 'Delegati Obiettivo II'),
    ('O', 'Delegati Obiettivo III'),
    ('P', 'Delegati Obiettivo IV'),
    ('Q', 'Delegati Obiettivo V'),
    ('R', 'Delegati Obiettivo VI'),
    ('S', 'Referenti di un’Attività di Area I'),
    ('T', 'Referenti di un’Attività di Area II'),
    ('U', 'Referenti di un’Attività di Area III'),
    ('V', 'Referenti di un’Attività di Area IV'),
    ('W', 'Referenti di un’Attività di Area V'),
    ('X', 'Referenti di un’Attività di Area VI'),
    ('Y', 'Delegati Autoparco'),
    ('Z', 'Delegati Formazione'),
    ('AA', 'Volontari aventi un dato titolo'),
)


# Dizionario 'Segmento' (key) => 'Filtro' (value)

SEGMENTI = {
    'Tutti gli utenti di Gaia':              lambda queryset: queryset,
    'Volontari':                             volontari,
    'Volontari da meno di un anno':          volontari_meno_un_anno,
    'Volontari da più di un anno':           volontari_piu_un_anno,
    'Volontari con meno di 35 anni':         volontari_meno_35_anni,
    'Volontari con 35 anni o più':           volontari_maggiore_o_uguale_35_anni,
    'Sostenitori CRI':                       sostenitori_cri,
    'Aspiranti volontari iscritti a un corso': aspiranti_volontari_iscritti_ad_un_corso,
    'Tutti i Presidenti':                    tutti_i_presidenti,
    'Presidenti di Comitati Locali':         presidenti_comitati_locali,
    'Presidenti di Comitati Regionali':      presidenti_comitati_regionali,
    'Delegati US':                           delegati_US,
    'Delegati Obiettivo I':                  delegati_Obiettivo_I,
    'Delegati Obiettivo II':                 delegati_Obiettivo_II,
    'Delegati Obiettivo III':                delegati_Obiettivo_III,
    'Delegati Obiettivo IV':                 delegati_Obiettivo_IV,
    'Delegati Obiettivo V':                  delegati_Obiettivo_V,
    'Delegati Obiettivo VI':                 delegati_Obiettivo_VI,
    'Referenti di un’Attività di Area I':    referenti_attivita_area_I,
    'Referenti di un’Attività di Area II':   referenti_attivita_area_II,
    'Referenti di un’Attività di Area III':  referenti_attivita_area_III,
    'Referenti di un’Attività di Area IV':   referenti_attivita_area_IV,
    'Referenti di un’Attività di Area V':    referenti_attivita_area_V,
    'Referenti di un’Attività di Area VI':   referenti_attivita_area_VI,
    'Delegati Autoparco':                    delegati_autoparco,
    'Delegati Formazione':                   delegati_formazione,
    'Volontari aventi un dato titolo':       volontari_con_titolo,
}
