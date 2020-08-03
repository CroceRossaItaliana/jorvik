from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now

from anagrafica.models import Appartenenza, Delega, Sede, Persona
from anagrafica.costanti import LOCALE, REGIONALE, LIMITE_ETA, LIMITE_ANNI_ATTIVITA
from anagrafica.permessi.applicazioni import (PRESIDENTE, COMMISSARIO, UFFICIO_SOCI,
    DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3,
    DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, REFERENTE,
    RESPONSABILE_AUTOPARCO, RESPONSABILE_FORMAZIONE)
from attivita.models import Attivita, Partecipazione


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
    operatore = 'gt' if meno else 'lte'
    data_limite = now()
    data_limite = data_limite.replace(year=data_limite.year - LIMITE_ETA).date()
    return queryset.filter(
        **{'data_nascita__{}'.format(operatore): data_limite}
    )


def _calcola_anni_attivita(queryset, meno=True):

    limite = now().replace(year=now().year - LIMITE_ANNI_ATTIVITA)
    if meno:
        appartenenze_filtrate = Appartenenza.query_attuale().filter(inizio__gte=limite)
    else:
        appartenenze_filtrate = Appartenenza.query_attuale().filter(inizio__lt=limite)

    return queryset.filter(appartenenze__in=appartenenze_filtrate)


# TODO: Aggiungere test per i filtri che utilizzano questa funzione
def _referenti_attivita(queryset, obiettivo=0):
    # TODO: Assicurarsi che questo filtro funzioni davvero!
    if obiettivo > 0:
        qs = queryset.filter(
            # Subquery per mischiarsi bene con le altre deleghe.
            pk__in=Persona.objects.filter(
                Delega.query_attuale(tipo=REFERENTE, oggetto_tipo=ContentType.objects.get_for_model(Attivita),
                                     oggetto_id__in=Attivita.objects.filter(
                                         area__obiettivo=obiettivo
                                     ).values_list('pk', flat=True)).via("delega")
            ).values_list('pk', flat=True)
        )
        return qs
    return queryset.none()


def _presidenze_comitati(queryset, estensione=LOCALE):
    sedi = Sede.objects.filter(attiva=True, tipo=Sede.COMITATO, estensione=estensione)
    return queryset.filter(delega__oggetto_tipo=ContentType.objects.get_for_model(Sede), delega__oggetto_id__in=sedi.values_list('id', flat=True))


# Filtri

def volontari(queryset):
    tutti_volontari = queryset.filter(appartenenze__membro=Appartenenza.VOLONTARIO)
    return _appartenenze_attive(tutti_volontari)


def volontari_meno_un_anno(queryset):
    tutti_volontari = volontari(queryset).filter()
    volontari_filtrati = _calcola_anni_attivita(tutti_volontari)
    return volontari_filtrati


def volontari_piu_un_anno(queryset):
    tutti_volontari = volontari(queryset).filter()
    volontari_filtrati = _calcola_anni_attivita(tutti_volontari, meno=False)
    return volontari_filtrati


def volontari_meno_35_anni(queryset):
    tutti_volontari = volontari(queryset)
    volontari_filtrati = _calcola_eta(tutti_volontari)
    return volontari_filtrati


def volontari_maggiore_o_uguale_35_anni(queryset):
    tutti_volontari = volontari(queryset)
    volontari_filtrati = _calcola_eta(tutti_volontari, meno=False)
    return volontari_filtrati


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


# funzione di supporto ricerca presidenti/commissari
def com_pres_all(queryset, tipo=PRESIDENTE):
    return queryset.filter(delega__tipo=tipo)


def tutti_i_presidenti(queryset):
    return com_pres_all(queryset, PRESIDENTE)


def presidenti_comitati_locali(queryset):
    return _presidenze_comitati(tutti_i_presidenti(queryset))


def presidenti_comitati_regionali(queryset):
    return _presidenze_comitati(tutti_i_presidenti(queryset), REGIONALE)


def tutti_i_commissari(queryset):
    return com_pres_all(queryset, COMMISSARIO)


def commissari_comitati_locali(queryset):
    return _presidenze_comitati(tutti_i_commissari(queryset))


def commissari_comitati_regionali(queryset):
    return _presidenze_comitati(tutti_i_commissari(queryset), REGIONALE)


def dipendenti(queryset):
    qs = queryset.filter(appartenenze__membro=Appartenenza.DIPENDENTE)
    return _appartenenze_attive(qs)


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


# TODO: Decidere come implementare il form per l'admin corrispondente
def volontari_con_titolo(queryset):
    return volontari(queryset).filter(titoli_personali__confermata=True)


def servizio_civile_universale(queryset):
    return queryset.filter(appartenenze__membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE)


NOMI_SEGMENTI = (
    ('A', 'Tutti gli utenti di Gaia'),
    ('B', 'Volontari'),
    ('C', 'Volontari da meno di un anno'),
    ('D', 'Volontari da più di un anno'),
    ('E', 'Volontari con meno di 33 anni'),
    ('F', 'Volontari con 33 anni o più'),
    ('G', 'Sostenitori CRI'),
    ('H', 'Aspiranti volontari iscritti a un corso'),
    ('I', 'Tutti i Presidenti'),
    ('J', 'Presidenti di Comitati Locali'),
    ('K', 'Presidenti di Comitati Regionali'),
    ('IC', 'Tutti i Commissari'),
    ('JC', 'Commissari di Comitati Locali'),
    ('KC', 'Commissari di Comitati Regionali'),
    ('L1', 'Dipendenti'),
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
    ('SC', 'Servizio civile universale')
)


# Dizionario 'Segmento' (key) => 'Filtro' (value)

SEGMENTI = {
    'A':              lambda queryset: queryset,
    'B':              volontari,
    'C':              volontari_meno_un_anno,
    'D':              volontari_piu_un_anno,
    'E':              volontari_meno_35_anni,
    'F':              volontari_maggiore_o_uguale_35_anni,
    'G':              sostenitori_cri,
    'H':              aspiranti_volontari_iscritti_ad_un_corso,
    'I':              tutti_i_presidenti,
    'IC':             tutti_i_commissari,
    'J':              presidenti_comitati_locali,
    'JC':             commissari_comitati_locali,
    'K':              presidenti_comitati_regionali,
    'KC':             commissari_comitati_regionali,
    'L1':             dipendenti,
    'L':              delegati_US,
    'M':              delegati_Obiettivo_I,
    'N':              delegati_Obiettivo_II,
    'O':              delegati_Obiettivo_III,
    'P':              delegati_Obiettivo_IV,
    'Q':              delegati_Obiettivo_V,
    'R':              delegati_Obiettivo_VI,
    'S':              referenti_attivita_area_I,
    'T':              referenti_attivita_area_II,
    'U':              referenti_attivita_area_III,
    'V':              referenti_attivita_area_IV,
    'W':              referenti_attivita_area_V,
    'X':              referenti_attivita_area_VI,
    'Y':              delegati_autoparco,
    'Z':              delegati_formazione,
    'AA':             volontari_con_titolo,
    'SC':             servizio_civile_universale
}
