from collections import OrderedDict

from formazione.elenchi import ElencoPartecipantiCorsiBase
from formazione.models import Corso
from ..permessi.costanti import LETTURA
from ..models import Delega
from ..profile import views


def filter_per_role(request, me, persona, sezioni):
    puo_leggere = me.permessi_almeno(persona, LETTURA)
    if not puo_leggere:
        return OrderedDict()

    # GAIA-213 (filtro aggiuntivo per direttori)
    corsi_direttore = Delega.corsi(me).filter(stato__in=[Corso.ATTIVO, Corso.PREPARAZIONE])
    corsi_persona = persona.corsi(corso_stato=[Corso.ATTIVO, Corso.PREPARAZIONE])
    corsi_in_comune = corsi_direttore & corsi_persona

    sezioni = OrderedDict(sezioni)
    if 'us' in request.GET or 'ea' in request.GET:
        return sezioni

    elif ElencoPartecipantiCorsiBase.SHORT_NAME in request.GET or corsi_in_comune:
        SEZIONI_VISIBILI_PER_DIRETTORE = ['appartenenze', 'curriculum',]

        # Trova corsi del direttore e corsi della persona
        if corsi_in_comune:
            menu_items = OrderedDict()
            for k, v in sezioni.items():
                if k in SEZIONI_VISIBILI_PER_DIRETTORE:
                    menu_items[k] = v
            return menu_items
        return OrderedDict()

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
