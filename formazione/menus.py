from django.core.urlresolvers import reverse

from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, ELENCHI_SOCI, RUBRICA_DELEGATI_OBIETTIVO_ALL, \
    GESTIONE_EVENTI_SEDE, GESTIONE_EVENTO


def to_show(me, permissions):
    if not me:
        return False

    if isinstance(permissions, list or tuple):
        for permission in permissions:
            if me.ha_permesso(permission):
                return True
    else:
        if me.ha_permesso(permissions):
            return True
    return False


def formazione_menu(menu_name, me=None):
    from curriculum.models import Titolo

    FORMAZIONE = (
        ("Corsi", (
            ("Attiva Corso", "fa-asterisk", reverse('formazione:new_course')) if to_show(me, GESTIONE_CORSI_SEDE) else None,
            ("Elenco Corsi", "fa-list", reverse('aspirante:corsi_base')),

            ("Attiva Evento", "fa-asterisk", reverse('formazione:evento_nuovo')) if to_show(me, GESTIONE_EVENTI_SEDE) else None,
            ("Gestione Eventi", "fa-list", reverse('formazione:evento_elenco')) if to_show(me, GESTIONE_EVENTO) else None,

            ("Domanda formativa", "fas fa-chart-pie", reverse('formazione:domanda')) if to_show(me, GESTIONE_CORSI_SEDE) else None,
            ('Catalogo Corsi', 'fa-list-alt', reverse('courses:catalog')),
            ('Acronimi', 'fa-book', '/page/glossario-corsi/'),
            ('Calendario', 'fa-calendar', reverse('formazione:formazione_calendar')),
            ('Regolamento Formazione', 'fa-file-alt', 'https://datafiles.gaia.cri.it/media/filer_public/08/59/0859cd54-ddad-4f26-8f8d-f48d2c92801d/regolamento_dei_corsi_di_formazione_per_volontari_e_dipendenti_della_croce_rossa_italiana.pdf'),
            ('Schema equipollenze Del. N° 66-20', 'fa-file-alt', 'https://datafiles.gaia.cri.it/media/filer_public/22/c4/22c446a7-d981-4cb9-be95-f6afec4b53d2/schema_per_equipollenze_del_66-20_per_gaia_1.pdf'),
            ('Schema equipollenze Del. N° 94-20', 'fa-file-alt', 'https://datafiles.gaia.cri.it/media/filer_public/a6/1b/a61b14e5-7286-4028-8aeb-255e0a4a7209/schema_per_equipollenze_94-20_per_gaia.pdf'),
            ('Albo Informatizzato', 'fa-list', reverse(
                'formazione:albo_info')) if to_show(
                me, RUBRICA_DELEGATI_OBIETTIVO_ALL + [GESTIONE_CORSI_SEDE]
            ) or (me and me.is_responsabile_area_albo_formazione) else None,
        )),
        ("Monitoraggio", (
            ("Fabbisogni Formativi Comitato Territoriale", 'fa-user',
             reverse('pages:monitoraggio-fabb-info-territoriale')) if ( me and (
                    me.is_presidente_o_commissario_territoriale or
                    me.is_responsabile_formazione_territoriale)) else None,
            ("Fabbisogni Formativi Comitato Regionale", 'fa-user',
             reverse('pages:monitoraggio-fabb-info-regionale')) if ( me and (
                    me.is_presidente_o_commissario_regionale or
                    me.is_responsabile_formazione_regionale)) else None,
            ("Monitora Fabbisogni Formativi Territoriali", 'fa-user',
             reverse('pages:monitora-fabb-info-territoriale')) if ( me and (
                    me.delega_presidente_e_commissario_regionale or
                    me.is_delgato_regionale_monitoraggio_fabbisogni_informativi
            )) else None,
            ("Monitora Fabbisogni Formativi", 'fa-user',
             reverse('pages:monitora-fabb-info-regionale')) if
                me and me.is_responsabile_formazione_nazionale else None

        )),
    )

    ASPIRANTE = (
        ("Aspirante", (
            ("Home page", "fa-home", reverse('aspirante:home')),
            ("Anagrafica", "fa-edit", reverse('utente:anagrafica')),
            ("Storico", "fa-clock-o", reverse('utente:storico')),
            ("Contatti", "fa-envelope", reverse('utente:contatti')),
            ("Fotografie", "fa-credit-card", reverse('utente:foto')),
            # ("Competenze personali", "fa-suitcase", reverse('utente:cv_tipo', args=[Titolo.COMPETENZA_PERSONALE])),
            ("Patenti Civili", "fa-car", reverse('utente:cv_tipo', args=[Titolo.PATENTE_CIVILE])),
            ("Titoli di Studio", "fa-graduation-cap", reverse('utente:cv_tipo', args=[Titolo.TITOLO_STUDIO])),
            ("Documenti Personali", "fa-graduation-cap", reverse('utente:documenti')),
        )),

        ("Nelle vicinanze", (
            ("Corsi di formazione", "fa-list", reverse('aspirante:corsi_base')),
            ("Sedi CRI", "fa-list", reverse('aspirante:sedi')),
            ("Impostazioni", "fa-gears", reverse('aspirante:settings')),
        )),

        ("Sicurezza", (
            ("Cambia password", "fa-key", reverse('utente:change_password')),
            ("Impostazioni Privacy", "fa-cogs", reverse('utente:privacy')),
        )),
    )

    # se l'utenza non ha la propia delegha, non puo vedere Monitoraggio
    formazione = puo_vedere_fabbisogni(me, FORMAZIONE)

    MENUS = dict(
        formazione=formazione,
        aspirante=ASPIRANTE,
    )
    return MENUS[menu_name]


def puo_vedere_fabbisogni(me, formazione):
    if me.is_presidente_o_commissario_territoriale or \
            me.is_presidente_o_commissario_regionale or \
            me.is_presidente_o_commissario_regionale or \
            me.is_responsabile_formazione_regionale or \
            me.delega_presidente_e_commissario_regionale or \
            me.is_delgato_regionale_monitoraggio_fabbisogni_informativi or \
            me.is_responsabile_formazione_nazionale:
        formazione = formazione
    else:
        formazione = list(formazione)
        formazione[1] = None
        formazione = tuple(formazione)
    return formazione
