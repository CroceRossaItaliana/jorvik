from django.core.urlresolvers import reverse


def sala_operativa(me):
    MENU_NAME = 'Sala Operativa'
    return (
        (MENU_NAME, (
            ("Reperibilità", "fa-user-plus", reverse('so:reperibilita')),
            ("Turni", "fa-user-plus", reverse('so:turni')),
            ("Poteri", "fa-user-plus", reverse('so:poteri')),
        )),
    )
