from django.core.urlresolvers import reverse

from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE, ELENCHI_SOCI


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
    FORMAZIONE = (
        ("Corsi", (
            ("Attiva Corso", "fa-asterisk", reverse('formazione:new_course')) if to_show(me, GESTIONE_CORSI_SEDE) else None,
            # ("Elenco Corsi", "fa-list", reverse('formazione:list_courses')),
            ("Domanda formativa", "fa-area-chart", reverse('formazione:domanda')) if to_show(me, GESTIONE_CORSI_SEDE) else None,
            ('Catalogo Corsi', 'fa-list-alt', '/page/catalogo-corsi/'),
            ('Glossario Corsi', 'fa-book', '/page/glossario-corsi/'),
            ('Albo Informatizzato', 'fa-list', reverse('formazione:albo_info')) if to_show(me, [ELENCHI_SOCI, GESTIONE_CORSI_SEDE]) else None,
        )),
    )

    ASPIRANTE = (
        ("Aspirante", (
            ("Home page", "fa-home", reverse('aspirante:home')),
            ("Anagrafica", "fa-edit", reverse('utente:anagrafica')),
            ("Storico", "fa-clock-o", reverse('utente:storico')),
            ("Contatti", "fa-envelope", reverse('utente:contatti')),
            ("Fotografie", "fa-credit-card", reverse('utente:foto')),
            ("Competenze personali", "fa-suitcase", reverse('utente:cv_tipo', args=['CP'])),
            ("Patenti Civili", "fa-car", reverse('utente:cv_tipo', args=['PP'])),
            ("Titoli di Studio", "fa-graduation-cap", reverse('utente:cv_tipo', args=['TS'])),
        )),

        ("Nelle vicinanze", (
            ("Corsi", "fa-list", reverse('aspirante:corsi_base')),
            ("Sedi CRI", "fa-list", reverse('aspirante:sedi')),
            ("Impostazioni", "fa-gears", reverse('aspirante:settings')),
        )),

        ("Sicurezza", (
            ("Cambia password", "fa-key", reverse('utente:change_password')),
            ("Impostazioni Privacy", "fa-cogs", reverse('utente:privacy')),
        )),
    )

    MENUS = dict(
        formazione=FORMAZIONE,
        aspirante=ASPIRANTE,
    )
    return MENUS[menu_name]
