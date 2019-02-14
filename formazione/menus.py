from django.core.urlresolvers import reverse


def formazione_menu(menu_name, gestione_corsi_sede):
    FORMAZIONE = (
        ("Corsi", (
            ("Attiva nuovo Corso", "fa-asterisk", reverse('formazione:new_course')) if gestione_corsi_sede else None,
            ("Elenco Corsi", "fa-list", reverse('formazione:list_courses')),
            ("Domanda formativa", "fa-area-chart", reverse('formazione:domanda')) if gestione_corsi_sede else None,
            ('Catalogo Corsi', 'fa-list-alt', '/page/catalogo-corsi/'),
            ('Glossario Corsi', 'fa-book', '/page/glossario-corsi/'),
            ('Albo Informatizzato', 'fa-list', reverse('formazione:albo_info')),
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
