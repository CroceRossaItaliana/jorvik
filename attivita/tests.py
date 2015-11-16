import datetime
from django.test import TestCase
from attivita.models import Attivita, Area, Turno
from anagrafica.costanti import LOCALE
from anagrafica.models import Sede, Persona, Appartenenza


class TestAttivita(TestCase):
    def test_attivita(self):

        ##Sicilia -> [Fiumefreddo, Mascali]
        ##Calabria ->[]

        sicilia = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        sicilia.save()

        fiumefreddo = Sede(
            nome="Comitato Locale di Fiumefreddo di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        fiumefreddo.save()

        mascali = Sede(
            nome="Comitato Locale di Mascali",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        mascali.save()

        calabria = Sede(
            nome="Comitato Regionale di Calabria",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        calabria.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=sicilia,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=sicilia,
            estensione=sicilia,
        )
        a.save()

        a1 = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=fiumefreddo,
            estensione=sicilia,
        )
        a1.save()

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

        t2 = Turno(
            attivita=a1,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30)
        )
        t2.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        p1 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIRAJDO",
            data_nascita="1994-2-5"
        )
        p1.save()

        p2 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJDO",
            data_nascita="1994-2-5"
        )
        p2.save()

        p3 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJMI",
            data_nascita="1994-2-5"
        )
        p3.save()

        app = Appartenenza(
            persona=p,
            sede=sicilia,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        app1 = Appartenenza(
            persona=p1,
            sede=fiumefreddo,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app1.save()

        app2 = Appartenenza(
            persona=p2,
            sede=mascali,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app2.save()

        app3 = Appartenenza(
            persona=p3,
            sede=calabria,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app3.save()

        self.assertTrue(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t.pk).exists(),
            msg="Il turno viene trovato nel calendario - attivita' creata dalla sede del volontario"
        )

        self.assertFalse(
            p.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t1.pk).exists(),
            msg="Il turno non viene trovato nel calendario - attivita' creata dalla sede del volontario"
        )


    def test_attivita_estesa(self):

        sicilia = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        sicilia.save()

        fiumefreddo = Sede(
            nome="Comitato Locale di Fiumefreddo di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        fiumefreddo.save()

        mascali = Sede(
            nome="Comitato Locale di Mascali",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
            genitore=sicilia,
        )
        mascali.save()

        calabria = Sede(
            nome="Comitato Regionale di Calabria",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
        )
        calabria.save()

        area = Area(
            nome="6",
            obiettivo=6,
            sede=sicilia,
        )
        area.save()

        a = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=sicilia,
            estensione=sicilia,
        )
        a.save()

        a1 = Attivita(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=fiumefreddo,
            estensione=sicilia,
        )
        a1.save()

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

        t2 = Turno(
            attivita=a1,
            prenotazione=datetime.datetime(2015, 11, 10),
            inizio=datetime.datetime(2015, 11, 10),
            fine=datetime.datetime(2015, 11, 30)
        )
        t2.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        p1 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIRAJDO",
            data_nascita="1994-2-5"
        )
        p1.save()

        p2 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJDO",
            data_nascita="1994-2-5"
        )
        p2.save()

        p3 = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJNOKAJMI",
            data_nascita="1994-2-5"
        )
        p3.save()

        app = Appartenenza(
            persona=p,
            sede=sicilia,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app.save()

        app1 = Appartenenza(
            persona=p1,
            sede=fiumefreddo,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app1.save()

        app2 = Appartenenza(
            persona=p2,
            sede=mascali,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app2.save()

        app3 = Appartenenza(
            persona=p3,
            sede=calabria,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        app3.save()

        self.assertTrue(
            p2.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t2.pk).exists(),
            msg="Il turno viene trovato nel calendario - attivita' estesa al volontario"
        )

        self.assertFalse(
            p3.calendario_turni(datetime.date(2015, 11, 1), datetime.date(2015, 11, 30)).filter(pk=t2.pk).exists(),
            msg="Il turno non viene trovato nel calendario - attivita' estesa al volontario"
        )
    