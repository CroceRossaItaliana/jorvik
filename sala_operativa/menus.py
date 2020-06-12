from django.core.urlresolvers import reverse


def sala_operativa(me):
    MENU_NAME = 'Sala Operativa'
    return (
        (MENU_NAME, (
            ("Reperibilità mie", 'fa-clock', reverse('so:reperibilita')),
            ("Reperibilità dei Volontari", 'fa-user', reverse('so:reperibilita_backup')),
            ("Turni", 'fa-calendar', reverse('so:turni')),
            ("Poteri", 'fa-magic', reverse('so:poteri')),
        )),
    )
