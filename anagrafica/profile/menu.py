from collections import OrderedDict

from ..models import Delega
from ..profile import views


def filter_per_role(me, persona, sezioni):
    sezioni = OrderedDict(sezioni)

    # GAIA-213 (filtro aggiuntivo per direttori)
    SEZIONI_VISIBILI_PER_DIRETTORE = ['appartenenze', 'curriculum']
    if me.is_direttore:
        menu_items = OrderedDict()
        # Trova corsi del direttore e corsi della persona
        corsi_in_comune = Delega.corsi(me) & persona.corsi

        # Se c'è almeno uno in comune - direttore potra vedere alcune sezioni
        if corsi_in_comune:
            for k, v in sezioni.items():
                if k in SEZIONI_VISIBILI_PER_DIRETTORE:
                    menu_items[k] = v
        return menu_items
    return sezioni


def profile_sections(puo_leggere, puo_modificare):
    """
    :param puo_leggere:
    :param puo_modificare:
    :return: generatore che contiene (path, (
        nome, icona, _funzione, permesso,
    ))
    """

    r = (
        ('anagrafica', (
            'Anagrafica', 'fa-edit', views._profilo_anagrafica, puo_leggere
        )),
        ('appartenenze', (
            'Appartenenze', 'fa-clock-o', views._profilo_appartenenze, puo_leggere
        )),
        ('deleghe', (
            'Deleghe', 'fa-clock-o', views._profilo_deleghe, puo_leggere
        )),
        ('turni', (
            'Turni', 'fa-calendar', views._profilo_turni, puo_leggere
        )),
        ('riserve', (
            'Riserve', 'fa-pause', views._profilo_riserve, puo_leggere
        )),
        ('fototessera', (
            'Fototessera', 'fa-photo', views._profilo_fototessera, puo_leggere
        )),
        ('documenti', (
            'Documenti', 'fa-folder', views._profilo_documenti, puo_leggere
        )),
        ('curriculum', (
            'Curriculum', 'fa-list', views._profilo_curriculum, puo_leggere
        )),
        ('sangue', (
            'Sangue', 'fa-flask', views._profilo_sangue, puo_modificare
        )),
        ('quote', (
            'Quote/Ricevute', 'fa-money', views._profilo_quote, puo_leggere
        )),
        ('provvedimenti', (
            'Provvedimenti', 'fa-legal', views._profilo_provvedimenti, puo_leggere
        )),
        ('credenziali', (
            'Credenziali', 'fa-key', views._profilo_credenziali, puo_modificare
        )),
    )

    return (x for x in r if len(x[1]) < 4 or x[1][3] == True)
