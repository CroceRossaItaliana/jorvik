import datetime

from django.test import TestCase
from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE
from anagrafica.forms import ModuloCreazioneEstensione
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Delega
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, PRESIDENTE
from anagrafica.permessi.costanti import MODIFICA, ELENCHI_SOCI
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede


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

    def test_permessi(self):

        c = Sede(
            nome="Comitato Regionale di Sicilia",
            tipo=Sede.COMITATO,
            estensione=REGIONALE,
        )
        c.save()

        c2 = Sede(
            genitore=c,
            nome="Comitato Provinciael di Catania",
            tipo=Sede.COMITATO,
            estensione=PROVINCIALE,
        )
        c2.save()

        p = Persona(
            nome="Mario",
            cognome="Rossi",
            codice_fiscale="FRSSAKJSIKAJDO",
            data_nascita="1994-2-5"
        )
        p.save()

        v = Persona(
            nome="Luigi",
            cognome="Verdi",
            codice_fiscale="FRXSAKJSIKAJDO",
            data_nascita="1995-2-5"
        )
        v.save()

        a = Appartenenza(
            persona=v,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        self.assertFalse(
            p.permessi_almeno(c, MODIFICA),
            msg="Questa persona non ha delega di presidenza"
        )

        self.assertFalse(
            p.permessi_almeno(v, MODIFICA),
            msg="Questa persona non ha delega di Ufficio Soci"
        )

        d1 = Delega(
            persona=p,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio="1980-12-10",
            fine="1990-12-10",
        )
        d1.save()

        self.assertFalse(
            p.permessi_almeno(v, MODIFICA),
            msg="La delega e' passata, non vale."
        )

        d2 = Delega(
            persona=p,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio="2020-12-10",
            fine="2025-12-10",
        )
        d2.save()

        self.assertFalse(
            p.permessi_almeno(v, MODIFICA),
            msg="La delega e' futura, non vale."
        )

        d3 = Delega(
            persona=p,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio="2020-12-10",
            fine=None,
        )
        d3.save()

        self.assertFalse(
            p.permessi_almeno(v, MODIFICA),
            msg="La delega e' futura, non vale."
        )

        self.assertFalse(
            p.oggetti_permesso(ELENCHI_SOCI).exists(),
            msg="Non ho permesso di Elenchi soci da nessuna parte"
        )

        d4 = Delega(
            persona=p,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio="2000-12-10",
            fine="2099-12-10",
        )
        d4.save()

        self.assertTrue(
            p.permessi_almeno(v, MODIFICA),
            msg="La persona ha diritti di US sulla scheda."
        )

        d4.delete()

        d5 = Delega(
            persona=p,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio="2000-12-10",
            fine=None,
        )
        d5.save()

        self.assertTrue(
            p.permessi_almeno(v, MODIFICA),
            msg="La persona ha diritti di US sulla scheda."
        )

        self.assertTrue(
            p.oggetti_permesso(ELENCHI_SOCI).count() == 2,
            msg="Ho permesso di elenchi su due comitati"
        )

        self.assertFalse(
            p.permessi_almeno(c, MODIFICA),
            msg="Questa persona non ha delega di presidenza"
        )

        d6 = Delega(
            persona=p,
            tipo=PRESIDENTE,
            oggetto=c,
            inizio="2000-12-10",
            fine=None,
        )
        d6.save()

        self.assertTrue(
            p.permessi_almeno(v, MODIFICA),
            msg="La persona ha diritti di US sulla scheda."
        )

        self.assertTrue(
            p.permessi_almeno(c, MODIFICA),
            msg="Questa persona ha delega di presidenza"
        )

        self.assertTrue(
            p.permessi_almeno(c2, MODIFICA),
            msg="Questa persona ha delega di presidenza, e puo' quindi modificare comitati sottostanti"
        )

        d5.delete()

        self.assertTrue(
            p.permessi_almeno(v, MODIFICA),
            msg="La persona ha ancora, tramite presidenza, diritti di US sulla scheda."
        )

        self.assertTrue(
            p.permessi_almeno(c, MODIFICA),
            msg="Questa persona ha delega di presidenza"
        )

        d6.fine = "2010-12-10"
        d6.save()

        self.assertFalse(
            p.permessi_almeno(v, MODIFICA),
            msg="La persona non ha piu, tramite presidenza, diritti di US sulla scheda."
        )

        self.assertFalse(
            p.permessi_almeno(c, MODIFICA),
            msg="Questa persona non ha piu delega di presidenza"
        )

        d6.delete()


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

    def test_estensione_accettata_accettata(self):
        presidente1 = crea_persona()
        presidente2 = crea_persona()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)

        sede2 = crea_sede(presidente2)

        self.assertTrue(
            da_estendere.estensione is None,
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        modulo = ModuloCreazioneEstensione()
        est = modulo.save(commit=False)
        est.richiedente = da_estendere
        est.persona = da_estendere
        est.destinazione = sede2
        est.save()
        est.richiedi()

        self.assertTrue(
            da_estendere.estensione == est,
            msg="L'estensione creata correttamente"
        )

        self.assertTrue(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        self.assertFalse(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        aut = presidente1.autorizzazioni_in_attesa().first()

        self.assertFalse(
            est.appartenenza is not None,
            msg="l'estensione non ha un'appartenenza"
        )

        modulo = est.autorizzazione_concedi_modulo()({
            "protocollo_numero": 31,
            "protocollo_data": datetime.date.today()
        })

        aut.concedi(presidente1, modulo=modulo)

        self.assertTrue(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni in attesa"
        )

        est.refresh_from_db()
        self.assertTrue(
            est.appartenenza is not None,
            msg="l'estensione ha un'appartenenza"
        )

        self.assertTrue(
            est.appartenenza.persona == da_estendere,
            msg="l'appartenenza contiene il volontario esatto"
        )

        self.assertTrue(
            est.appartenenza.sede == sede2,
            msg="l'appartenenza contiene la sede esatta"
        )

        self.assertTrue(
            est.appartenenza.membro == Appartenenza.ESTESO,
            msg="l'appartenenza e' di tipo esteso"
        )

        self.assertTrue(
            est.appartenenza.esito == Appartenenza.ESITO_PENDING,
            msg="l'appartenenza e' pendente"
        )

        aut2 = presidente2.autorizzazioni_in_attesa().first()

        aut2.concedi(presidente2)

        self.assertTrue(
            est.appartenenza.esito == Appartenenza.ESITO_OK,
            msg="l'appartenenza e' accettata"
        )

    def test_estensione_accettata_negata(self):
        presidente1 = crea_persona()
        presidente2 = crea_persona()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)

        sede2 = crea_sede(presidente2)

        self.assertTrue(
            da_estendere.estensione is None,
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        modulo = ModuloCreazioneEstensione()
        est = modulo.save(commit=False)
        est.richiedente = da_estendere
        est.persona = da_estendere
        est.destinazione = sede2
        est.save()
        est.richiedi()

        self.assertTrue(
            da_estendere.estensione == est,
            msg="L'estensione creata correttamente"
        )

        self.assertTrue(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        self.assertFalse(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        aut = presidente1.autorizzazioni_in_attesa().first()

        self.assertFalse(
            est.appartenenza is not None,
            msg="l'estensione non ha un'appartenenza"
        )

        modulo = est.autorizzazione_concedi_modulo()({
            "protocollo_numero": 31,
            "protocollo_data": datetime.date.today()
        })
        aut.concedi(presidente1, modulo=modulo)

        self.assertTrue(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni in attesa"
        )

        est.refresh_from_db()
        self.assertTrue(
            est.appartenenza is not None,
            msg="l'estensione ha un'appartenenza"
        )

        self.assertTrue(
            est.appartenenza.persona == da_estendere,
            msg="l'appartenenza contiene il volontario esatto"
        )

        self.assertTrue(
            est.appartenenza.sede == sede2,
            msg="l'appartenenza contiene la sede esatta"
        )

        self.assertTrue(
            est.appartenenza.membro == Appartenenza.ESTESO,
            msg="l'appartenenza e' di tipo esteso"
        )

        self.assertTrue(
            est.appartenenza.esito == Appartenenza.ESITO_PENDING,
            msg="l'appartenenza e' pendente"
        )

        aut2 = presidente2.autorizzazioni_in_attesa().first()

        aut2.nega(presidente2)

        self.assertTrue(
            est.appartenenza.esito == Appartenenza.ESITO_NO,
            msg="l'appartenenza e' rifiutata"
        )


    def test_estensione_negata(self):

        presidente1 = crea_persona()
        presidente2 = crea_persona()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)

        sede2 = crea_sede(presidente2)

        self.assertTrue(
            da_estendere.estensione is None,
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        modulo = ModuloCreazioneEstensione()
        est = modulo.save(commit=False)
        est.richiedente = da_estendere
        est.persona = da_estendere
        est.destinazione = sede2
        est.save()
        est.richiedi()

        
        
        self.assertTrue(
            da_estendere.estensione == est,
            msg="L'estensione creata correttamente"
        )

        self.assertTrue(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente ha autorizzazioni da processare"
        )

        self.assertFalse(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )

        aut = presidente1.autorizzazioni_in_attesa().first()

        self.assertFalse(
            est.appartenenza is not None,
            msg="l'estensione non ha un'appartenenza"
        )

        aut.nega(presidente1, motivo="Il volontario qualcosa")


        est.refresh_from_db()
        self.assertFalse(
            est.appartenenza is not None,
            msg="l'estensione non ha un'appartenenza"
        )

        self.assertIsNone(
            da_estendere.estensione,
            msg="Il volontario non ha estensioni in corso"
        )

        self.assertTrue(
            est.esito == est.ESITO_NO,
            msg="Estensione rifiutata"
        )
