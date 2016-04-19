from anagrafica.models import Appartenenza


def volontari(queryset):
    return queryset.filter(appartenenze__membro=Appartenenza.VOLONTARIO)


def volontari_meno_un_anno(queryset):
    return volontari(queryset).filter()


def volontari_piu_un_anno(queryset):
    return volontari(queryset).filter()


def volontari_meno_35_anni(queryset):
    return volontari(queryset).filter()


def volontari_maggiore_o_uguale_35_anni(queryset):
    return volontari(queryset).filter()


def sostenitori_cri(queryset):
    return queryset.filter(appartenenze__membro=Appartenenza.SOSTENITORE)


def aspiranti_volontari_iscritti_ad_un_corso(queryset):
    pass


def tutti_i_presidenti(queryset):
    pass


def presidenti_comitati_locali(queryset):
    pass


def presidenti_comitati_regionali(queryset):
    pass


def delegati_US(queryset):
    pass


def delegati_Obiettivo_I(queryset):
    pass


def delegati_Obiettivo_II(queryset):
    pass


def delegati_Obiettivo_III(queryset):
    pass


def delegati_Obiettivo_IV(queryset):
    pass


def delegati_Obiettivo_V(queryset):
    pass


def delegati_Obiettivo_VI(queryset):
    pass


def referenti_attivita_area_I(queryset):
    pass


def referenti_attivita_area_II(queryset):
    pass


def referenti_attivita_area_III(queryset):
    pass


def referenti_attivita_area_IV(queryset):
    pass


def referenti_attivita_area_V(queryset):
    pass


def referenti_attivita_area_VI(queryset):
    pass


def delegati_autoparco(queryset):
    pass


def delegati_formazione(queryset):
    pass


def volontari_con_titolo(queryset):
    return volontari(queryset).filter()


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


SEGMENTI = {
    'Tutti gli utenti di Gaia': lambda queryset: queryset,
    'Volontari': volontari,
    'Volontari da meno di un anno': volontari_meno_un_anno,
    'Volontari da più di un anno': volontari_piu_un_anno,
    'Volontari con meno di 35 anni': volontari_meno_35_anni,
    'Volontari con 35 anni o più': volontari_maggiore_o_uguale_35_anni,
    'Sostenitori CRI': sostenitori_cri,
    'Aspiranti volontari iscritti a un corso': aspiranti_volontari_iscritti_ad_un_corso,
    'Tutti i Presidenti': tutti_i_presidenti,
    'Presidenti di Comitati Locali': presidenti_comitati_locali,
    'Presidenti di Comitati Regionali': presidenti_comitati_regionali,
    'Delegati US': delegati_US,
    'Delegati Obiettivo I': delegati_Obiettivo_I,
    'Delegati Obiettivo II': delegati_Obiettivo_II,
    'Delegati Obiettivo III': delegati_Obiettivo_III,
    'Delegati Obiettivo IV': delegati_Obiettivo_IV,
    'Delegati Obiettivo V': delegati_Obiettivo_V,
    'Delegati Obiettivo VI': delegati_Obiettivo_VI,
    'Referenti di un’Attività di Area I': referenti_attivita_area_I,
    'Referenti di un’Attività di Area II': referenti_attivita_area_II,
    'Referenti di un’Attività di Area III': referenti_attivita_area_III,
    'Referenti di un’Attività di Area IV': referenti_attivita_area_IV,
    'Referenti di un’Attività di Area V': referenti_attivita_area_V,
    'Referenti di un’Attività di Area VI': referenti_attivita_area_VI,
    'Delegati Autoparco': delegati_autoparco,
    'Delegati Formazione': delegati_formazione,
    'Volontari aventi un dato titolo': volontari_con_titolo,
}
