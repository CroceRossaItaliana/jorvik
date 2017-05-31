from datetime import datetime, timedelta

from base.utils import poco_fa
from donazioni.models import Campagna


def crea_campagna(sede, nome='Test Campagna', inizio=None):
    if not inizio:
        inizio = poco_fa()
    fine = inizio + timedelta(days=30)
    c = Campagna(nome=nome, organizzatore=sede,
                 descrizione='Campagna di Test',
                 inizio=inizio, fine=fine)
    c.save()
    return c
