import datetime
from django.test import TestCase
from attivita.models import Attivita, Area, Turno
from anagrafica.costanti import LOCALE
from anagrafica.models import Sede, Persona, Appartenenza


class TestAttivita(TestCase):
    def test_attivita(self):


        s = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        s.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=s,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=s,
            estensione=s,
        )
        a.save()

        t = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30),
            minimo=1,
            massimo=6,
        )
        t.save()

        t1 = Turno(
            attivita=a,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 10, 10),
            fine=datetime.datetime(2015, 10, 30)
        )
        t1.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        app = Appartenenza(
            persona=p,
            sede=s,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        self.assertTrue(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t.pk).exists(),
            msg="Il turno viene trovato nel calendario"
        )

        self.assertFalse(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t1.pk).exists(),
            msg="Il turno non viene trovato nel calendario"
        )
