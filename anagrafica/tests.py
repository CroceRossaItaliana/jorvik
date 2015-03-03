from django.test import TestCase
from anagrafica.models import Comitato, Persona, Appartenenza


class TestAnagrafica(TestCase):

    def test_appartenenza(self):

        c = Comitato(
            nome="Comitato Regionale di Sicilia",
            tipo=Comitato.COMITATO,
            estensione=Comitato.LOCALE,
        )
        c.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        a = Appartenenza(
            persona=p,
            comitato=c,
            inizio="1980-12-10",
            confermata=False
        )
        a.save()
        #a.richiedi() # TODO Necessario presidente.

        self.assertTrue(
            c.appartenenze_attuali().count() == 0,
            msg="Non ci devono essere appartenze ancora attuali"
        )

        #for x in a.autorizzazioni:
        #    x.concedi(p)

        #self.assertTrue("Ora invece si", c.appartenenze_attuali())