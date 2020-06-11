from django.core.urlresolvers import reverse


def sala_operativa(me):
    MENU_NAME = 'Sala Operativa'
    return (
        (MENU_NAME, (
            ("Reperibilità", 'fa-clock', reverse('so:reperibilita')),
            ("Turni", 'fa-calendar', reverse('so:turni')),
            ("Poteri", 'fa-magic', reverse('so:poteri')),
        )),
    )
