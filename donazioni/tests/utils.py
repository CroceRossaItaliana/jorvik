from datetime import datetime, timedelta

from anagrafica.permessi.applicazioni import RESPONSABILE_CAMPAGNA
from base.utils import poco_fa
from donazioni.models import Campagna


def crea_campagna(sede, nome='Test Campagna', inizio=None):
    if not inizio:
        inizio = poco_fa()
    fine = inizio + timedelta(days=365)
    c = Campagna(nome=nome, organizzatore=sede,
                 descrizione='Campagna di Test',
                 inizio=inizio, fine=fine)
    c.save()
    return c


def aggiungi_responsabile_campagna(campagna, persona):
    campagna.aggiungi_delegato(RESPONSABILE_CAMPAGNA, persona)


def mock_autonow():
    return datetime(2016, 1, 1)
