from django.test import TestCase
from anagrafica.costanti import LOCALE
from anagrafica.models import Sede, Persona, Appartenenza, Documento


class TestAnagrafica(TestCase):

    def test_appartenenza(self):

        c = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=LOCALE,
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
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=False
        )
        a.save()

        self.assertTrue(
            c.appartenenze_attuali().count() == 0,
            msg="Non ci devono essere appartenze ancora attuali."
        )

        a.richiedi()

        self.assertTrue(
            c.appartenenze_attuali().count() == 0,
            msg="Non ancora."
        )

        self.assertTrue(
            a.autorizzazioni_set(),
            msg="Qualche autorizzazione e' stata generata."

        )

        a.autorizzazioni_set()[0].concedi(p)

        self.assertTrue(
            c.appartenenze_attuali().count() == 1,
            msg="Ora l'appartenenza e' attuale."
        )

        # Riscarica l'appartenenza
        a = Appartenenza.objects.get(pk=a.id)

        self.assertTrue(
            a.confermata,
            msg="L'appartenenza risulta ora confermata."
        )

        self.assertTrue(
            a.attuale(),
            msg="L'appartenenza risulta ora attuale ad oggi."
        )

        self.assertTrue(
            c.membri_attuali()[0] == p,
            msg="Il membro attuale corrisponde alla persona inserita."
        )

        self.assertTrue(
            c.appartenenze_attuali(membro=Appartenenza.MILITARE).count() == 0,
            msg="Ma ancora nessun militare."
        )

    def test_documenti(self):

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJD1",
            data_nascita="1994-2-5"
        )
        p.save()

        d = Documento(
            persona=p,
            tipo=Documento.PATENTE_CIVILE,
            file=None,
        )
        d.save()

        self.assertTrue(
            p.documenti.all(),
            msg="Il membro ha almeno un documento"
        )

        self.assertTrue(
            p.documenti.filter(tipo=Documento.PATENTE_CIVILE),
            msg="Il membro ha di fatto una patente civile"
        )

        self.assertFalse(
            p.documenti.filter(tipo=Documento.CARTA_IDENTITA),
            msg="Il membro non ha davvero alcuna carta di identita"
        )

