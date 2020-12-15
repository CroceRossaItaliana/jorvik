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

    def delete_sessions(request):
        session_names = ['us', 'ea',]
        for n in session_names:
            if n in request.session.keys():
                # print(n)
                del request.session[n]

    def elenco_shortname_in_get():
        for i in [ElencoPartecipantiCorsiBase.SHORT_NAME,]:
            if i in request.GET and not corsi_in_comune:
                return False
        return True

    sezioni = OrderedDict(sezioni)
    if 'us' in request.GET or 'ea' in request.GET:
        if 'us' in request.GET:
            request.session['us'] = ''
        elif 'ea' in request.GET:
            request.session['ea'] = ''
        return sezioni

    elif 'us' in request.session.keys() and not elenco_shortname_in_get():
        delete_sessions(request)
        return sezioni

    elif 'ea' in request.session.keys() and not elenco_shortname_in_get():
        delete_sessions(request)
        return sezioni

    elif ElencoPartecipantiCorsiBase.SHORT_NAME in request.GET or corsi_in_comune:
        delete_sessions(request)

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
            'Appartenenze', 'fa-map', views._profilo_appartenenze, puo_leggere
        )),
        ('deleghe', (
            'Deleghe', 'fa-user-clock', views._profilo_deleghe, puo_leggere
        )),
        ('turni', (
            'Turni', 'fa-calendar', views._profilo_turni, puo_leggere
        )),
        ('riserve', (
            'Riserve', 'fa-pause', views._profilo_riserve, puo_leggere
        )),
        ('fototessera', (
            'Fototessera', 'fa-image', views._profilo_fototessera, puo_leggere
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
            'Quote/Ricevute', 'fa-money-bill-alt', views._profilo_quote, puo_leggere
        )),
        ('provvedimenti', (
            'Provvedimenti', 'fa-balance-scale-right', views._profilo_provvedimenti, puo_leggere
        )),
        ('credenziali', (
            'Credenziali', 'fa-key', views._profilo_credenziali, puo_modificare
        )),
    )

    return (x for x in r if len(x[1]) < 4 or x[1][3] == True)
