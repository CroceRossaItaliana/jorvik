import datetime

from django.test import TestCase
from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, TERRITORIALE
from anagrafica.forms import ModuloCreazioneEstensione, ModuloNegaEstensione
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Delega
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, PRESIDENTE
from anagrafica.permessi.costanti import MODIFICA, ELENCHI_SOCI
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza


class TestAnagrafica(TestCase):

    def test_appartenenza(self):

        p = crea_persona()
        c = crea_sede()

        self.assertTrue(
            c.appartenenze_attuali().count() == 0,
            msg="Non ci devono essere appartenze ancora attuali."
        )

        a = crea_appartenenza(p, c)
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

        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        c2 = crea_sede(estensione=TERRITORIALE, genitore=c)
        c2.save()

        p = crea_persona()
        p.save()

        v = crea_persona()
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

        p = crea_persona()
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

    def test_estensione_accettata(self):
        presidente1 = crea_persona()
        presidente2 = crea_persona()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)

        sede2 = crea_sede(presidente2)

        self.assertFalse(
            da_estendere.estensioni_attuali_e_in_attesa().exists(),
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
            da_estendere.estensioni_attuali_e_in_attesa().exists(),
            msg="L'estensione creata correttamente"
        )

        self.assertFalse(
            da_estendere.estensioni_attuali().exists(),
            msg="L'estensione creata correttamente (in attesa, non attuale)"
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

        self.assertFalse(
            presidente2.autorizzazioni_in_attesa().exists(),
            msg="Il presidente di dest. non ha autorizzazioni in attesa"
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
            est.appartenenza.esito == Appartenenza.ESITO_OK,
            msg="l'appartenenza e' accettata"
        )


    def test_estensione_negata(self):

        presidente1 = crea_persona()
        presidente2 = crea_persona()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)

        sede2 = crea_sede(presidente2)

        self.assertFalse(
            da_estendere.estensioni_attuali_e_in_attesa().exists(),
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
            da_estendere.estensioni_attuali_e_in_attesa().filter(pk=est.pk).exists(),
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

        aut.nega(presidente1, modulo=ModuloNegaEstensione({"motivo": "Un motivo qualsiasi"}))


        est.refresh_from_db()
        self.assertFalse(
            est.appartenenza is not None,
            msg="l'estensione non ha un'appartenenza"
        )

        self.assertTrue(
            est.esito == est.ESITO_NO,
            msg="Estensione rifiutata"
        )

        da_estendere.refresh_from_db()
        self.assertFalse(
            da_estendere.estensioni_attuali().exists(),
            msg="Il volontario non ha estensioni in corso"
        )

    def test_comitato(self):
        """
        Controlla che il Comitato venga ottenuto correttamente.
        """

        italia = crea_sede(estensione=NAZIONALE)
        self.assertTrue(
            italia.comitato == italia,
            msg="Il Comitato Nazionale e' Comitato di se' stesso"
        )

        sicilia = crea_sede(estensione=REGIONALE, genitore=italia)
        self.assertTrue(
            sicilia.comitato == sicilia,
            msg="Il Comitato Regionale e' Comitato di se' stesso"
        )

        catania = crea_sede(estensione=PROVINCIALE, genitore=sicilia)
        self.assertTrue(
            catania.comitato == catania,
            msg="Il Comitato Provinciale e' Comitato di se' stesso"
        )

        giarre = crea_sede(estensione=LOCALE, genitore=catania)
        self.assertTrue(
            giarre.comitato == giarre,
            msg="Il Comitato Locale e' Comitato di se' stesso"
        )

        riposto = crea_sede(estensione=TERRITORIALE, genitore=giarre)
        self.assertTrue(
            riposto.comitato == giarre,
            msg="Unita' territoriale di Locale funziona correttamente"
        )

        maletto = crea_sede(estensione=TERRITORIALE, genitore=catania)
        self.assertTrue(
            maletto.comitato == catania,
            msg="Unita' territoriale di Provinciale funziona corretatmente"
        )

        self.assertTrue(
            maletto.comitato == catania.comitato,
            msg="Sede.comitato e' transitiva"
        )

    def test_sede_espandi(self):

        italia = crea_sede(estensione=NAZIONALE)
        _sicilia = crea_sede(estensione=REGIONALE, genitore=italia)
        __catania = crea_sede(estensione=PROVINCIALE, genitore=_sicilia)
        ___maletto = crea_sede(estensione=TERRITORIALE, genitore=__catania)
        ___giarre = crea_sede(estensione=LOCALE, genitore=__catania)
        ____riposto = crea_sede(estensione=TERRITORIALE, genitore=___giarre)
        ____salfio = crea_sede(estensione=TERRITORIALE, genitore=___giarre)
        lombardia = crea_sede(estensione=REGIONALE, genitore=italia)
        _milano = crea_sede(estensione=PROVINCIALE, genitore=lombardia)

        # Ricarica tutte le Sedi dal database
        for x in [italia, _sicilia, __catania, ___maletto, ___giarre, ____riposto, ____salfio, lombardia, _milano]:
            x.refresh_from_db()


        self.assertTrue(
            italia.espandi(includi_me=True, pubblici=True).count() == (italia.get_descendants().count() + 1),
            msg="Espansione dal Nazionale ritorna tutti i Comitati - inclusa Italia",
        )

        self.assertTrue(
            italia.espandi(includi_me=True, pubblici=False).count() == 1,
            msg="Espansione dal Nazionale solo se stessa se pubblici=False",
        )

        self.assertTrue(
            italia.espandi(includi_me=False, pubblici=True).count() == italia.get_descendants().count(),
            msg="Espansione dal Nazionale ritorna tutti i Comitati - escludendo Italia",
        )

        self.assertTrue(
            _sicilia.espandi(includi_me=True, pubblici=True).count() == (_sicilia.get_descendants().count() + 1),
            msg="Espansione dal Regionale ritrna tutti i Comitati - Inclusa Regione"
        )

        self.assertTrue(
            _sicilia.espandi(includi_me=True, pubblici=False).count() == 1,
            msg="Espansione dal Regionale ritrna solo se stessa se pubblici=False"
        )

        self.assertTrue(
            __catania in _sicilia.espandi(pubblici=True),
            msg="Espansione Regionale ritorna Provinciale"
        )

        self.assertTrue(
            ____salfio in _sicilia.espandi(pubblici=True),
            msg="Espansione Regionale ritorna Territoriale"
        )

        self.assertTrue(
            ____riposto in ___giarre.espandi(pubblici=True),
            msg="Espansione Locale ritorna Territoriale"
        )

        self.assertTrue(
            ____riposto in ___giarre.espandi(pubblici=False),
            msg="Espansione Locale ritorna Territoriale"
        )

        self.assertTrue(
            ____riposto not in __catania.espandi(),
            msg="Espansione Provinciale non ritorna territoriale altrui"
        )

        self.assertTrue(
            ___maletto in __catania.espandi(),
            msg="Espansione Provinciale ritorna territoriale proprio"
        )



