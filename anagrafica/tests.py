import datetime
from unittest import skipIf

import re
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from django.utils.timezone import now
from freezegun import freeze_time
from lxml import html

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, TERRITORIALE
from anagrafica.forms import ModuloCreazioneEstensione, ModuloNegaEstensione, ModuloProfiloModificaAnagrafica, \
    ModuloConsentiTrasferimento
from anagrafica.models import Appartenenza, Documento, Delega, Dimissione, Estensione, Trasferimento, Riserva, Sede
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, PRESIDENTE, UFFICIO_SOCI_UNITA, DELEGATO_OBIETTIVO_1, \
    DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4, DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, \
    DELEGATO_AREA, UFFICIO_SOCI, UFFICIO_SOCI_UNITA, RESPONSABILE_AREA, REFERENTE, REFERENTE_GRUPPO, DELEGATO_CO, \
    RESPONSABILE_FORMAZIONE, DIRETTORE_CORSO, RESPONSABILE_AUTOPARCO
from anagrafica.permessi.costanti import MODIFICA, ELENCHI_SOCI, LETTURA, GESTIONE_SOCI
from anagrafica.utils import termina_deleghe_giovani
from anagrafica.viste import _rubrica_delegati
from autenticazione.models import Utenza
from autenticazione.utils_test import TestFunzionale
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, email_fittizzia, \
    crea_utenza
from formazione.models import Aspirante, CorsoBase, PartecipazioneCorsoBase
from posta.models import Messaggio, Autorizzazione
from ufficio_soci.forms import ModuloElencoVolontari


class TestAnagrafica(TestCase):

    def test_appartenenza_modificabile_con_campo_precedente(self):

        persona = crea_persona()
        sede1 = crea_sede()
        sede2 = crea_sede()

        # appartenenza "isolata"
        a_persona_1 = crea_appartenenza(persona, sede1)
        self.assertTrue(a_persona_1.modificabile())

        # doppia appartenenza "aperta" genera blocchi (perché non consistente)
        a_persona_2 = crea_appartenenza(persona, sede2)
        a_persona_2.inizio = "1980-11-10"
        a_persona_1.precedente = a_persona_2
        a_persona_1.save()
        a_persona_2.save()
        self.assertFalse(a_persona_1.modificabile())

        # Se l'appartenenza è terminata, quella più recente non è modificabile
        a_persona_2.terminazione = Appartenenza.TRASFERIMENTO
        a_persona_2.save()
        a_persona_1.refresh_from_db()
        a_persona_2.refresh_from_db()
        self.assertFalse(a_persona_1.modificabile())

        # Se è un trasferimento o altro non si può modificare
        for tipo in Appartenenza.TERMINAZIONE:
            if tipo[0] not in Appartenenza.MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI:
                for membro in Appartenenza.MEMBRO:
                    if membro[0] not in Appartenenza.PRECEDENZE_MODIFICABILI:
                        a_persona_2.terminazione = tipo[0]
                        a_persona_2.membro = membro[0]
                        a_persona_2.save()
                        a_persona_1.refresh_from_db()
                        a_persona_2.refresh_from_db()
                        self.assertFalse(a_persona_1.modificabile())

    def test_appartenenza_modificabile_con_precedente_per_data(self):

        persona = crea_persona()
        sede1 = crea_sede()
        sede2 = crea_sede()

        # appartenenza "isolata"
        a_persona_1 = crea_appartenenza(persona, sede1)
        self.assertTrue(a_persona_1.modificabile())

        corso = CorsoBase.objects.create(
            sede=sede1, data_inizio=poco_fa(), data_esame=poco_fa(), progressivo=1, anno=poco_fa().year
        )
        # Corso non completato non genera blocchi
        partecipazione = PartecipazioneCorsoBase.objects.create(persona=persona, corso=corso)
        self.assertTrue(a_persona_1.modificabile())

        # se deriva da un corso base non è modificabile
        partecipazione.esito_esame = PartecipazioneCorsoBase.IDONEO
        partecipazione.save()
        self.assertFalse(a_persona_1.modificabile())

        partecipazione.esito_esame = None
        partecipazione.save()
        self.assertTrue(a_persona_1.modificabile())

        # Se è un'estensione non si può modificare
        a_persona_1.membro = Appartenenza.ESTESO
        self.assertFalse(a_persona_1.modificabile())

        # Se è un dipendente si può modificare
        a_persona_1.membro = Appartenenza.DIPENDENTE
        self.assertTrue(a_persona_1.modificabile())

        # Se è un ordinario si può modificare
        a_persona_1.membro = Appartenenza.ORDINARIO
        self.assertTrue(a_persona_1.modificabile())

        # Se è un sostenitore si può modificare
        a_persona_1.membro = Appartenenza.SOSTENITORE
        self.assertTrue(a_persona_1.modificabile())

        # doppia appartenenza "aperta" genera blocchi (perché non consistente)
        a_persona_1.membro = Appartenenza.VOLONTARIO
        a_persona_2 = crea_appartenenza(persona, sede2)
        a_persona_2.inizio = "1980-11-10"
        a_persona_1.save()
        a_persona_2.save()
        self.assertFalse(a_persona_1.modificabile())

        # Se l'appartenenza è terminata, quella più recente non è modificabile
        a_persona_2.terminazione = Appartenenza.TRASFERIMENTO
        a_persona_2.fine = "1980-12-10"
        a_persona_2.save()
        a_persona_1.refresh_from_db()
        a_persona_2.refresh_from_db()
        self.assertFalse(a_persona_1.modificabile())

        # Se è un trasferimento o altro non si può modificare
        for tipo in Appartenenza.TERMINAZIONE:
            if tipo[0] not in Appartenenza.MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI:
                for membro in Appartenenza.MEMBRO:
                    if membro[0] not in Appartenenza.PRECEDENZE_MODIFICABILI:
                        a_persona_2.terminazione = tipo[0]
                        a_persona_2.membro = membro[0]
                        a_persona_2.save()
                        a_persona_1.refresh_from_db()
                        a_persona_2.refresh_from_db()
                        self.assertFalse(a_persona_1.modificabile())

    def test_appartenenza_modificabile_controllo_nuovo_inizio(self):

        persona = crea_persona()
        sede1 = crea_sede()
        sede2 = crea_sede()

        # appartenenza "isolata"
        a_persona_1 = crea_appartenenza(persona, sede1)
        self.assertTrue(a_persona_1.modificabile())

        # doppia appartenenza "aperta" genera blocchi (perché non consistente)
        a_persona_2 = crea_appartenenza(persona, sede2)
        a_persona_2.inizio = "1980-11-10"
        a_persona_1.save()
        a_persona_2.save()
        self.assertFalse(a_persona_1.modificabile())

        # Se l'appartenenza è terminata, quella più recente non è modificabile
        a_persona_2.terminazione = Appartenenza.TRASFERIMENTO
        a_persona_2.fine = "1980-12-10"
        a_persona_2.save()
        a_persona_1.refresh_from_db()
        a_persona_2.refresh_from_db()
        self.assertFalse(a_persona_1.modificabile())

        # Se è una dimissione si può modificare se la data di inizio è successiva alla terminazione
        a_persona_2.terminazione = Appartenenza.DIMISSIONE
        a_persona_2.membro = Appartenenza.VOLONTARIO
        a_persona_2.save()
        a_persona_1.refresh_from_db()
        a_persona_2.refresh_from_db()
        self.assertTrue(a_persona_1.modificabile())
        self.assertTrue(a_persona_1.modificabile(a_persona_2.fine + datetime.timedelta(days=10)))
        self.assertFalse(a_persona_1.modificabile(a_persona_2.fine - datetime.timedelta(days=10)))

        # Se è una espulsione si può modificare se la data di inizio è successiva alla terminazione
        a_persona_2.terminazione = Appartenenza.ESPULSIONE
        a_persona_2.membro = Appartenenza.VOLONTARIO
        a_persona_2.save()
        a_persona_1.refresh_from_db()
        a_persona_2.refresh_from_db()
        self.assertTrue(a_persona_1.modificabile())
        self.assertTrue(a_persona_1.modificabile(a_persona_2.fine + datetime.timedelta(days=10)))
        self.assertFalse(a_persona_1.modificabile(a_persona_2.fine - datetime.timedelta(days=10)))

        data_corso = a_persona_2.fine - datetime.timedelta(days=10)
        corso = CorsoBase.objects.create(
            sede=sede1, data_inizio=data_corso, data_esame=data_corso, progressivo=1, anno=data_corso.year
        )
        # Corso non completato non genera blocchi
        partecipazione = PartecipazioneCorsoBase.objects.create(persona=persona, corso=corso)
        self.assertTrue(a_persona_1.modificabile())

        # se il corso base è prima delle dimissioni viene ignorato
        partecipazione.esito_esame = PartecipazioneCorsoBase.IDONEO
        partecipazione.save()
        self.assertTrue(a_persona_1.modificabile())

        partecipazione.esito_esame = None
        partecipazione.save()

        data_corso = a_persona_2.fine + datetime.timedelta(days=10)
        corso.data_inizio = data_corso
        corso.save()
        self.assertTrue(a_persona_1.modificabile())

        # se il corso base è dopo le dimissioni blocca il cambio data
        partecipazione.esito_esame = PartecipazioneCorsoBase.IDONEO
        partecipazione.save()
        self.assertFalse(a_persona_1.modificabile())

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


    def test_dimissione(self):
        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        p = crea_persona()
        p.save()

        a = Appartenenza(
            persona=p,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        d = Dimissione(
            persona=p,
            sede=c,
            appartenenza=a
        )
        d.save()

        self.assertTrue(
            a.attuale(),
            msg="L'appartenenza risulta quella attuale."
        )

        d.applica()

        self.assertFalse(
            a.attuale(),
            msg="L'appartenenza risulta non più attuale."
        )

        appartenenze_attuali = p.appartenenze_attuali()

        self.assertTrue(
            appartenenze_attuali.count() == 0,
            msg="Non esiste alcuna appartenenza attuale per dimissioni normali."
        )

    def test_dimissione_passaggio_sostenitore(self):
        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        p = crea_persona()
        p.save()

        a = Appartenenza(
            persona=p,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        d = Dimissione(
            persona=p,
            sede=c,
            appartenenza=a
        )
        d.save()

        self.assertTrue(
            a.attuale(),
            msg="L'appartenenza risulta quella attuale."
        )

        d.applica(trasforma_in_sostenitore=True)

        self.assertFalse(
            a.attuale(),
            msg="L'appartenenza risulta non più attuale."
        )

        appartenenze_attuali = p.appartenenze_attuali()

        self.assertTrue(
            appartenenze_attuali.count() == 1,
            msg="Esiste solo una appartenenza attuale come sostenitore."
        )

    #@skipIf(not GOOGLE_KEY, "Nessuna chiave API Google per testare la ricerca su Maps.")
    @freeze_time('2016-11-14')
    def test_storia_volontario(self):
        presidente1 = crea_persona()
        presidente2 = crea_persona()

        persona = crea_persona()
        persona.save()

        persona, sede1, app1 = crea_persona_sede_appartenenza(presidente1)
        sede2 = crea_sede(presidente2)
        sede2.save()
        sede3 = crea_sede(presidente2)
        sede3.save()

        # Appena diventato volontario
        a = Appartenenza(
            persona=persona,
            sede=sede1,
            membro=Appartenenza.VOLONTARIO,
            inizio=poco_fa(),
            confermata=True
        )
        a.save()

        self.assertTrue(persona.volontario_da_meno_di_un_anno)

        # data vecchia nel passato
        a.inizio = "1980-12-10"
        a.save()
        self.assertFalse(persona.volontario_da_meno_di_un_anno)
        
        # trasferiscilo ad altro comitato

        modulo = ModuloCreazioneEstensione()
        est = modulo.save(commit=False)
        est.richiedente = persona
        est.persona = persona
        est.destinazione = sede2
        est.save()
        est.richiedi()
        aut = presidente1.autorizzazioni_in_attesa().first()
        modulo = est.autorizzazione_concedi_modulo()({
            "protocollo_numero": 31,
            "protocollo_data": datetime.date.today()
        })
        aut.concedi(presidente1, modulo=modulo)
        est.refresh_from_db()

        # il trasferimento non cambia l'anzianità
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # impostiamo una data recente
        a.inizio = datetime.date.today()
        a.save()
        self.assertTrue(persona.volontario_da_meno_di_un_anno)

        # trasferimento fallito ad altro comitato
        modulo = ModuloCreazioneEstensione()
        est = modulo.save(commit=False)
        est.richiedente = persona
        est.persona = persona
        est.destinazione = sede3
        est.save()
        est.richiedi()
        aut = presidente1.autorizzazioni_in_attesa().first()
        modulo = est.autorizzazione_concedi_modulo()({
            "protocollo_numero": 32,
            "protocollo_data": datetime.date.today()
        })
        aut.nega(presidente1, modulo=modulo)
        est.refresh_from_db()

        # lo stato non è cambiato
        self.assertTrue(persona.volontario_da_meno_di_un_anno)

        # data vecchia nel passato
        a.inizio = "1980-12-10"
        a.save()
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # un espulso non è più un volontario, quindi deve fallire
        a.inizio = datetime.date.today()
        a.save()
        persona.espelli()
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # reintegriamo l'utente
        a = Aspirante(persona=persona)
        a.locazione = sede1.locazione
        a.save()

        # l'aspirante non è volontario
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # promosso a volontario
        persona.da_aspirante_a_volontario(sede2)
        # è appena tornato volontario
        self.assertTrue(persona.volontario_da_meno_di_un_anno)

        # dimettiamolo
        for app in persona.appartenenze_attuali():
            d = Dimissione(
                persona=persona,
                sede=sede2,
                appartenenza=app
            )
            d.save()
            d.applica()
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # reintegriamo l'utente
        a = Aspirante(persona=persona)
        a.locazione = sede1.locazione
        a.save()

        # l'aspirante non è volontario
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

        # promosso a volontario
        persona.da_aspirante_a_volontario(sede2)
        # è appena tornato volontario
        self.assertTrue(persona.volontario_da_meno_di_un_anno)

        attuale = persona.appartenenze_attuali().get(membro=Appartenenza.VOLONTARIO)
        # data vecchia nel passato
        attuale.inizio = "1980-12-10"
        attuale.save()
        self.assertFalse(persona.volontario_da_meno_di_un_anno)

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

    def test_estensione_non_automatica(self):
        presidente1 = crea_persona()
        presidente1.email_contatto = email_fittizzia()
        presidente1.save()
        presidente2 = crea_persona()
        presidente2.email_contatto = email_fittizzia()
        presidente2.save()

        da_estendere, sede1, app1 = crea_persona_sede_appartenenza(presidente1)
        da_estendere.email_contatto = email_fittizzia()
        da_estendere.save()

        ufficio_soci = crea_persona()
        ufficio_soci.email_contatto = email_fittizzia()
        ufficio_soci.save()
        crea_appartenenza(ufficio_soci, sede1)
        Delega.objects.create(persona=ufficio_soci, tipo=UFFICIO_SOCI, oggetto=sede1, inizio=poco_fa())

        sede2 = crea_sede(presidente2)

        self.assertFalse(
            da_estendere.estensioni_attuali_e_in_attesa().exists(),
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )
        ora = now()

        est = Estensione.objects.create(
            destinazione=sede2,
            persona=da_estendere,
            richiedente=da_estendere,
            motivo='test'
        )
        self.assertEqual(0, Autorizzazione.objects.count())
        est.richiedi()
        self.assertNotIn(est, Estensione.con_esito_ok())
        self.assertEqual(1, Autorizzazione.objects.count())
        self.assertEqual(2, len(mail.outbox))

        # Notifica Presidente in uscita
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Richiesta di Estensione da %s' % da_estendere.nome_completo) > -1)
        self.assertTrue(presidente1.email_contatto in email.to)

        # Notifica Presidente in entrata
        email = mail.outbox[1]
        self.assertTrue(email.subject.find('Notifica di Estensione in entrata') > -1)
        self.assertTrue(presidente2.email_contatto in email.to)

        autorizzazione = Autorizzazione.objects.first()

        autorizzazione.scadenza = ora - datetime.timedelta(days=10)
        autorizzazione.save()
        self.assertFalse(autorizzazione.concessa)
        self.assertEqual(da_estendere.appartenenze_attuali(membro=Appartenenza.ESTESO, sede=sede2).count(), 0)

        Autorizzazione.gestisci_automatiche()
        autorizzazione.refresh_from_db()

        # Estensioni non sono approvate in automatico
        self.assertEqual(2, len(mail.outbox))

        self.assertEqual(autorizzazione.concessa, None)
        self.assertFalse(autorizzazione.oggetto.automatica)
        Autorizzazione.gestisci_automatiche()
        self.assertEqual(autorizzazione.concessa, None)
        self.assertNotIn(est, Estensione.con_esito_ok())
        self.assertEqual(da_estendere.appartenenze_attuali(membro=Appartenenza.ESTESO, sede=sede2).count(), 0)

    def test_trasferimento_automatico(self):
        presidente1 = crea_persona()
        presidente1.email_contatto = email_fittizzia()
        presidente1.save()
        presidente2 = crea_persona()
        presidente2.email_contatto = email_fittizzia()
        presidente2.save()

        da_trasferire, sede1, app1 = crea_persona_sede_appartenenza(presidente1)
        da_trasferire.email_contatto = email_fittizzia()
        da_trasferire.save()

        ufficio_soci = crea_persona()
        ufficio_soci.email_contatto = email_fittizzia()
        ufficio_soci.save()
        crea_appartenenza(ufficio_soci, sede1)
        Delega.objects.create(persona=ufficio_soci, tipo=UFFICIO_SOCI, oggetto=sede1, inizio=poco_fa())

        sede2 = crea_sede(presidente2)

        self.assertFalse(
            da_trasferire.estensioni_attuali_e_in_attesa().exists(),
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )
        ora = now()

        trasf = Trasferimento.objects.create(
            destinazione=sede2,
            persona=da_trasferire,
            richiedente=da_trasferire,
            motivo='test'
        )
        self.assertEqual(0, Autorizzazione.objects.count())
        trasf.richiedi()
        self.assertNotIn(trasf, Trasferimento.con_esito_ok())
        self.assertEqual(1, Autorizzazione.objects.count())
        self.assertEqual(1, len(mail.outbox))

        # Notifica Presidente in uscita
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Richiesta di trasferimento da %s' % da_trasferire.nome_completo) > -1)
        self.assertTrue(presidente1.email_contatto in email.to)

        autorizzazione = Autorizzazione.objects.first()

        autorizzazione.scadenza = ora - datetime.timedelta(days=10)
        autorizzazione.save()
        self.assertFalse(autorizzazione.concessa)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede1).count(), 1)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede2).count(), 0)

        Autorizzazione.gestisci_automatiche()
        autorizzazione.refresh_from_db()

        self.assertEqual(5, len(mail.outbox))
        destinatari_verificati = 0
        for email in mail.outbox[1:]:
            if da_trasferire.email_contatto in email.to:
                # Notifica alla persona trasferita
                self.assertTrue(email.subject.find('Richiesta di trasferimento APPROVATA') > -1)
                destinatari_verificati += 1
            elif presidente1.email_contatto in email.to or ufficio_soci.email_contatto in email.to or presidente2.email_contatto in email.to:
                # Notifica presidente e ufficio soci in uscita
                self.assertTrue(email.subject.find('Richiesta di trasferimento da %s APPROVATA' % da_trasferire.nome_completo) > -1)
                self.assertTrue(email.body.find('articolo 9.5 del "Regolamento') > -1)
                self.assertTrue(email.body.find('automaticamente.') > -1)
                self.assertFalse(email.body.find(presidente1.nome_completo) > -1)
                self.assertTrue(email.body.find('La richiesta di trasferimento inoltrata il {}'.format(ora.strftime('%d/%m/%Y'))) > -1)
                destinatari_verificati += 1
        self.assertEqual(destinatari_verificati, 4)

        trasf.refresh_from_db()
        autorizzazione.refresh_from_db()
        self.assertTrue(autorizzazione.concessa)
        self.assertTrue(autorizzazione.automatica)
        self.assertTrue(trasf.automatica)
        self.assertTrue(autorizzazione.oggetto.automatica)
        Autorizzazione.gestisci_automatiche()
        trasf.refresh_from_db()
        autorizzazione.refresh_from_db()
        self.assertTrue(autorizzazione.concessa)
        self.assertIn(trasf, Trasferimento.con_esito_ok())
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede1).count(), 0)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede2).count(), 1)

    def test_trasferimento_manuale(self):
        presidente1 = crea_persona()
        presidente1.email_contatto = email_fittizzia()
        presidente1.save()
        presidente2 = crea_persona()
        presidente2.email_contatto = email_fittizzia()
        presidente2.save()

        da_trasferire, sede1, app1 = crea_persona_sede_appartenenza(presidente1)
        da_trasferire.email_contatto = email_fittizzia()
        da_trasferire.save()

        ufficio_soci = crea_persona()
        ufficio_soci.email_contatto = email_fittizzia()
        ufficio_soci.save()
        crea_appartenenza(ufficio_soci, sede1)
        Delega.objects.create(persona=ufficio_soci, tipo=UFFICIO_SOCI, oggetto=sede1, inizio=poco_fa())

        sede2 = crea_sede(presidente2)

        self.assertFalse(
            da_trasferire.estensioni_attuali_e_in_attesa().exists(),
            msg="Non esiste estensione alcuna"
        )

        self.assertFalse(
            presidente1.autorizzazioni_in_attesa().exists(),
            msg="Il presidente non ha autorizzazioni in attesa"
        )
        ora = now()

        trasf = Trasferimento.objects.create(
            destinazione=sede2,
            persona=da_trasferire,
            richiedente=da_trasferire,
            motivo='test'
        )
        self.assertEqual(0, Autorizzazione.objects.count())
        trasf.richiedi()
        self.assertNotIn(trasf, Trasferimento.con_esito_ok())
        self.assertEqual(1, Autorizzazione.objects.count())
        self.assertEqual(1, len(mail.outbox))

        # Notifica Presidente in uscita
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Richiesta di trasferimento da %s' % da_trasferire.nome_completo) > -1)
        self.assertTrue(email.body.find('Nota bene: Questa richiesta di trasferimento') > -1)
        self.assertTrue(presidente1.email_contatto in email.to)

        autorizzazione = Autorizzazione.objects.first()

        self.assertFalse(autorizzazione.concessa)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede1).count(), 1)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede2).count(), 0)

        form = ModuloConsentiTrasferimento(
            {'protocollo_data': now().date().strftime('%Y-%m-%d'), 'protocollo_numero': 1}
        )
        form.is_valid()
        autorizzazione.concedi(firmatario=presidente1, modulo=form)
        autorizzazione.refresh_from_db()
        trasf.refresh_from_db()

        self.assertEqual(5, len(mail.outbox))
        destinatari_verificati = 0
        for email in mail.outbox[1:]:
            if da_trasferire.email_contatto in email.to:
                # Notifica alla persona trasferita
                self.assertTrue(email.subject.find('Richiesta di trasferimento APPROVATA') > -1)
                destinatari_verificati += 1
            elif presidente1.email_contatto in email.to or ufficio_soci.email_contatto in email.to or presidente2.email_contatto in email.to:
                # Notifica presidente e ufficio soci in uscita
                self.assertTrue(email.subject.find('Richiesta di trasferimento da %s APPROVATA' % da_trasferire.nome_completo) > -1)
                self.assertFalse(email.body.find('articolo 9.5 del "Regolamento') > -1)
                self.assertTrue(email.body.find(presidente1.nome_completo) > -1)
                self.assertTrue(email.body.find('Nota bene: Questa richiesta di trasferimento') == -1)
                self.assertTrue(email.body.find('La richiesta di trasferimento inoltrata il {}'.format(ora.strftime('%d/%m/%Y'))) > -1)
                destinatari_verificati += 1
        self.assertEqual(destinatari_verificati, 4)

        trasf.refresh_from_db()
        autorizzazione.refresh_from_db()
        self.assertTrue(autorizzazione.concessa)
        self.assertFalse(autorizzazione.automatica)
        self.assertFalse(trasf.automatica)
        self.assertFalse(autorizzazione.oggetto.automatica)
        Autorizzazione.gestisci_automatiche()
        trasf.refresh_from_db()
        autorizzazione.refresh_from_db()
        self.assertTrue(autorizzazione.concessa)
        self.assertIn(trasf, Trasferimento.con_esito_ok())
        self.assertFalse(trasf.automatica)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede1).count(), 0)
        self.assertEqual(da_trasferire.appartenenze_attuali(membro=Appartenenza.VOLONTARIO, sede=sede2).count(), 1)

    def test_cron_notifiche(self):

        presidente1 = crea_persona()
        presidente1.email_contatto = email_fittizzia()
        presidente1.save()
        presidente2 = crea_persona()
        presidente2.email_contatto = email_fittizzia()
        presidente2.save()

        trasferire_1, sede1, app1 = crea_persona_sede_appartenenza(presidente1)
        trasferire_1.email_contatto = email_fittizzia()
        trasferire_1.save()

        trasferire_2 = crea_persona()
        trasferire_2.email_contatto = email_fittizzia()
        trasferire_2.save()
        crea_appartenenza(trasferire_2, sede1)

        trasferire_3 = crea_persona()
        trasferire_3.email_contatto = email_fittizzia()
        trasferire_3.save()
        crea_appartenenza(trasferire_3, sede1)

        estendere = crea_persona()
        estendere.email_contatto = email_fittizzia()
        estendere.save()
        crea_appartenenza(estendere, sede1)

        ufficio_soci = crea_persona()
        ufficio_soci.email_contatto = email_fittizzia()
        ufficio_soci.save()
        crea_appartenenza(ufficio_soci, sede1)
        Delega.objects.create(persona=ufficio_soci, tipo=UFFICIO_SOCI, oggetto=sede1, inizio=poco_fa())

        sede2 = crea_sede(presidente2)

        trasf_auto = Trasferimento.objects.create(
            destinazione=sede2,
            persona=trasferire_1,
            richiedente=trasferire_1,
            motivo='test'
        )
        trasf_auto.richiedi()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Richiesta di trasferimento da {}'.format(trasferire_1.nome_completo))
        self.assertEqual(mail.outbox[0].to, [presidente1.email_contatto])
        mail.outbox = []

        trasf_manuale = Trasferimento.objects.create(
            destinazione=sede2,
            persona=trasferire_2,
            richiedente=trasferire_2,
            motivo='test'
        )
        trasf_manuale.richiedi()
        trasf_manuale.automatica = False
        for autorizzazione in trasf_manuale.autorizzazioni:
            autorizzazione.scadenza = None
            autorizzazione.tipo_gestione = Autorizzazione.MANUALE
            autorizzazione.save()
        trasf_manuale.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Richiesta di trasferimento da {}'.format(trasferire_2.nome_completo))
        self.assertEqual(mail.outbox[0].to, [presidente1.email_contatto])

        trasf_manuale = Trasferimento.objects.create(
            destinazione=sede2,
            persona=trasferire_3,
            richiedente=trasferire_3,
            motivo='test'
        )
        trasf_manuale.richiedi()
        trasf_manuale.automatica = False
        trasf_manuale.save()
        for autorizzazione in trasf_manuale.autorizzazioni:
            autorizzazione.scadenza = None
            autorizzazione.tipo_gestione = Autorizzazione.MANUALE
            autorizzazione.save()
            autorizzazione.nega(presidente1, auto=False)

        trasf_manuale = Trasferimento.objects.create(
            destinazione=sede2,
            persona=trasferire_3,
            richiedente=trasferire_3,
            motivo='test'
        )
        trasf_manuale.richiedi()
        trasf_manuale.automatica = False
        trasf_manuale.ritirata = True
        trasf_manuale.save()
        for autorizzazione in trasf_manuale.autorizzazioni:
            autorizzazione.scadenza = None
            autorizzazione.tipo_gestione = Autorizzazione.MANUALE
            autorizzazione.save()

        mail.outbox = []

        estensione = Estensione.objects.create(
            destinazione=sede2,
            persona=estendere,
            richiedente=estendere,
            motivo='test'
        )
        estensione.richiedi()
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Richiesta di Estensione da {}'.format(estendere.nome_completo))
        self.assertEqual(mail.outbox[0].to, [presidente1.email_contatto])
        self.assertEqual(mail.outbox[1].subject, 'Notifica di Estensione in entrata')
        self.assertEqual(mail.outbox[1].to, [presidente2.email_contatto])
        mail.outbox = []

        Autorizzazione.notifiche_richieste_in_attesa()
        self.assertEqual(len(mail.outbox), 2)

        for email in mail.outbox:
            self.assertEqual(email.subject, 'Richieste in attesa di approvazione')
            self.assertTrue(email.to == [presidente1.email_contatto] or email.to, [ufficio_soci.email_contatto])
            self.assertTrue('Estensioni' in email.body)
            self.assertTrue('Trasferimenti' in email.body)
            self.assertTrue('Data di approvazione automatica' in email.body)
            self.assertTrue(estendere.nome_completo in email.body)
            self.assertTrue(trasferire_2.nome_completo in email.body)
            self.assertTrue(trasferire_1.nome_completo in email.body)
            self.assertTrue(trasferire_3.nome_completo not in email.body)

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

    def test_permessi_ufficio_soci(self):

        stefano = crea_persona()
        catania = crea_sede(presidente=stefano, estensione=LOCALE)
        maletto = crea_sede(estensione=TERRITORIALE, genitore=catania)

        ufficio_soci_catania_locale = crea_persona()
        Delega.objects.create(persona=ufficio_soci_catania_locale, tipo=UFFICIO_SOCI, oggetto=catania, inizio=poco_fa())

        ufficio_soci_catania_unita = crea_persona()
        Delega.objects.create(persona=ufficio_soci_catania_unita, tipo=UFFICIO_SOCI_UNITA, oggetto=catania, inizio=poco_fa())

        ufficio_soci_maletto = crea_persona()
        Delega.objects.create(persona=ufficio_soci_maletto, tipo=UFFICIO_SOCI_UNITA, oggetto=maletto, inizio=poco_fa())

        self.assertTrue(
            ufficio_soci_catania_locale.oggetti_permesso(GESTIONE_SOCI).filter(pk=catania.pk),
            msg="US Catania Locale puo' gestire soci Catania"
        )

        self.assertTrue(
            ufficio_soci_catania_locale.oggetti_permesso(GESTIONE_SOCI).filter(pk=maletto.pk),
            msg="US Catania Locale puo' gestire soci Maletto"
        )

        self.assertTrue(
            ufficio_soci_catania_unita.oggetti_permesso(GESTIONE_SOCI).filter(pk=catania.pk),
            msg="US Catania Unita puo' gestire soci Catania"
        )

        self.assertFalse(
            ufficio_soci_catania_unita.oggetti_permesso(GESTIONE_SOCI).filter(pk=maletto.pk),
            msg="US Catania Unita NON puo' gestire soci Maletto"
        )

        self.assertFalse(
            ufficio_soci_maletto.oggetti_permesso(GESTIONE_SOCI).filter(pk=catania.pk),
            msg="US Maletto NON puo' gestire soci Catania"
        )

        self.assertTrue(
            ufficio_soci_maletto.oggetti_permesso(GESTIONE_SOCI).filter(pk=maletto.pk),
            msg="US Maletto puo' gestire soci Maletto"
        )


        # Inizialmente nessuno ha autorizzazioni
        self.assertFalse(
            ufficio_soci_catania_locale.autorizzazioni_in_attesa().exists()
            or ufficio_soci_catania_unita.autorizzazioni_in_attesa().exists()
            or ufficio_soci_maletto.autorizzazioni_in_attesa().exists()
            or stefano.autorizzazioni_in_attesa().exists(),
            msg="Inizialmente nessuno ha autorizzzioni in attesa"
        )

        tizio_nuovo = crea_persona()
        app = Appartenenza.objects.create(persona=tizio_nuovo, membro=Appartenenza.VOLONTARIO, inizio=poco_fa(), sede=maletto)
        app.richiedi()


        self.assertFalse(
            ufficio_soci_catania_unita.autorizzazioni_in_attesa().exists(),
            msg="Il delegato Catania Unita non vede la richiesta"
        )

        self.assertTrue(
            ufficio_soci_catania_locale.autorizzazioni_in_attesa().exists(),
            msg="Il delegato Catania Locale vede la richiesta"
        )

        self.assertTrue(
            ufficio_soci_maletto.autorizzazioni_in_attesa().exists(),
            msg="Il delegato Maletto vede la richiesta"
        )

        # Accettiamo la richiesta.
        for x in app.autorizzazioni.all():
            x.concedi(stefano, modulo=None)

        self.assertFalse(
            ufficio_soci_catania_unita.permessi_almeno(tizio_nuovo, MODIFICA),
            msg="Il delegato Catania Unita non puo gestire volontario"
        )

        self.assertFalse(
            ufficio_soci_catania_unita.permessi_almeno(tizio_nuovo, LETTURA),
            msg="Il delegato Catania Unita non puo gestire volontario"
        )

        self.assertTrue(
            ufficio_soci_catania_locale.permessi_almeno(tizio_nuovo, MODIFICA),
            msg="Il delegato Catania Locale puo gestire volontario"
        )

        self.assertTrue(
            ufficio_soci_maletto.permessi_almeno(tizio_nuovo, MODIFICA),
            msg="Il delegato Maletto puo gestire volontario"
        )

    def test_riserva_nel_passato(self):

        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)
        crea_utenza(persona, email=email_fittizzia())

        self.client.login(username=persona.utenza.email, password='prova')

        dati = {
            'inizio': poco_fa(),
            'fine': poco_fa() + datetime.timedelta(days=30),
            'motivo': 'test'
        }
        response = self.client.post('/utente/riserva/', data=dati)
        self.assertContains(response, 'Non può essere richiesta una riserva per una data nel passato')
        self.assertFalse(Riserva.objects.filter(persona=persona).exists())

        dati = {
            'inizio': poco_fa() + datetime.timedelta(days=10),
            'fine': poco_fa() + datetime.timedelta(days=30),
            'motivo': 'test'
        }
        response = self.client.post('/utente/riserva/', data=dati)
        self.assertNotContains(response, 'Non può essere richiesta una riserva per una data nel passato')
        self.assertTrue(Riserva.objects.filter(persona=persona).exists())

    def test_termina_delegati_giovani(self):
        presidente = crea_persona()
        sede = crea_sede(presidente)

        meno_di_33 = now().replace(year=now().year - 32)
        piu_di_33 = now().replace(year=now().year - 34)

        persona_1 = crea_persona()
        persona_1.data_nascita = piu_di_33
        persona_1.email_contatto = email_fittizzia()
        persona_1.save()
        persona_2 = crea_persona()
        persona_2.data_nascita = meno_di_33
        persona_2.email_contatto = email_fittizzia()
        persona_2.save()

        Delega.objects.create(tipo=DELEGATO_OBIETTIVO_5, persona=persona_1, oggetto=sede, firmatario=presidente, inizio=now())
        Delega.objects.create(tipo=DELEGATO_OBIETTIVO_5, persona=persona_2, oggetto=sede, firmatario=presidente, inizio=now())

        self.assertEqual(persona_1.deleghe_attuali(tipo=DELEGATO_OBIETTIVO_5).count(), 1)
        self.assertEqual(persona_2.deleghe_attuali(tipo=DELEGATO_OBIETTIVO_5).count(), 1)

        self.assertEqual(len(mail.outbox), 0)

        termina_deleghe_giovani()

        self.assertEqual(persona_1.deleghe_attuali(tipo=DELEGATO_OBIETTIVO_5).count(), 0)
        self.assertEqual(persona_2.deleghe_attuali(tipo=DELEGATO_OBIETTIVO_5).count(), 1)

        self.assertEqual(len(mail.outbox), 1)

    def test_dimission_decesso(self):

        presidente = crea_persona()
        presidente.email_contatto = email_fittizzia()
        presidente.save()
        crea_utenza(presidente, presidente.email_contatto, 'presidente')
        sede = crea_sede(presidente)
        ut = Sede.objects.create(
            nome="Unita Terr",
            tipo=Sede.COMITATO,
            estensione=TERRITORIALE,
            genitore=sede,
        )
        persona_1 = crea_persona()
        persona_1.email_contatto = email_fittizzia()
        persona_1.save()
        Delega.objects.create(tipo=UFFICIO_SOCI, persona=persona_1, oggetto=sede, firmatario=presidente, inizio=now())
        crea_utenza(persona_1, persona_1.email_contatto, 'persona_1')

        persona_2 = crea_persona()
        persona_2.email_contatto = email_fittizzia()
        persona_2.save()
        Delega.objects.create(tipo=UFFICIO_SOCI_UNITA, persona=persona_2, oggetto=ut, firmatario=presidente, inizio=now())
        crea_utenza(persona_2, persona_2.email_contatto, 'persona_2')

        persona_deceduta = crea_persona()
        Appartenenza.objects.create(
            persona=persona_deceduta, membro=Appartenenza.VOLONTARIO, inizio=now(), sede=ut
        )
        persona_deceduta.email_contatto = email_fittizzia()
        persona_deceduta.save()

        persona_deceduta_2 = crea_persona()
        Appartenenza.objects.create(
            persona=persona_deceduta_2, membro=Appartenenza.VOLONTARIO, inizio=now(), sede=sede
        )
        persona_deceduta_2.email_contatto = email_fittizzia()
        persona_deceduta_2.save()

        self.client.login(username=presidente.utenza.email, password='presidente')
        dati = {
            'motivo': Dimissione.DECEDUTO,
            'info': 'test',
        }
        response = self.client.post('/us/dimissioni/{}/'.format(persona_deceduta.pk), data=dati)
        self.assertContains(response, 'non sarà inviata alcuna notifica')

        self.assertEqual(len(mail.outbox), 2)
        self.assertFalse(persona_deceduta.email_contatto in [email.to for email in mail.outbox])
        self.assertTrue("Dimissioni per decesso" in mail.outbox[0].subject)
        self.assertTrue("Presidente" in mail.outbox[0].body)
        self.assertTrue("Ufficio Soci" in mail.outbox[0].body)
        self.assertTrue("recupero di tesserino e divisa" in mail.outbox[0].body)
        mail.outbox = []

        response = self.client.post('/us/dimissioni/{}/'.format(persona_deceduta_2.pk), data=dati)
        self.assertContains(response, 'non sarà inviata alcuna notifica')

        self.assertEqual(len(mail.outbox), 2)
        self.assertFalse(persona_deceduta_2.email_contatto in [email.to for email in mail.outbox])
        self.assertTrue("Dimissioni per decesso" in mail.outbox[0].subject)
        self.assertTrue("Presidente" in mail.outbox[0].body)
        self.assertTrue("Ufficio Soci" in mail.outbox[0].body)
        self.assertTrue("recupero di tesserino e divisa" in mail.outbox[0].body)

    def test_rubriche_delegati(self):
        italia = crea_sede(estensione=NAZIONALE)
        toscana = crea_sede(estensione=REGIONALE, genitore=italia)
        veneto = crea_sede(estensione=REGIONALE, genitore=italia)
        emilia_romagna = crea_sede(estensione=REGIONALE, genitore=italia)
        abruzzo = crea_sede(estensione=REGIONALE, genitore=italia)
        firenze = crea_sede(estensione=PROVINCIALE, genitore=toscana)
        dicomano = crea_sede(estensione=TERRITORIALE, genitore=firenze)
        empoli = crea_sede(estensione=LOCALE, genitore=toscana)
        vinci = crea_sede(estensione=TERRITORIALE, genitore=empoli)

        sedi_tutte = Sede.objects.filter(pk__in=(
            italia.pk, toscana.pk, veneto.pk, emilia_romagna.pk, abruzzo.pk, firenze.pk, dicomano.pk, empoli.pk,
            vinci.pk)
        )
        sedi_toscana = Sede.objects.filter(pk__in=(
            toscana.pk, firenze.pk, dicomano.pk, empoli.pk, vinci.pk)
        )
        sedi_firenze = Sede.objects.filter(pk__in=(firenze.pk, dicomano.pk))
        sede_firenze = Sede.objects.filter(pk__in=(firenze.pk,))
        sede_dicomano = Sede.objects.filter(pk__in=(dicomano.pk,))
        sedi_empoli = Sede.objects.filter(pk__in=(empoli.pk, vinci.pk))
        sede_vinci = Sede.objects.filter(pk__in=(vinci.pk,))
        sedi_abruzzo = Sede.objects.filter(pk__in=(abruzzo.pk,))

        delegato_nazionale = crea_persona()
        delegato_nazionale_no_6 = crea_persona()
        delegato_toscana = crea_persona()
        delegato_firenze = crea_persona()
        delegato_firenze_no_5 = crea_persona()
        delegato_dicomano = crea_persona()
        delegato_empoli = crea_persona()
        delegato_vinci = crea_persona()
        delegato_veneto = crea_persona()
        delegato_emilia_romagna = crea_persona()
        delegato_abruzzo = crea_persona()
        Delega.objects.create(persona=delegato_nazionale, tipo=DELEGATO_OBIETTIVO_6, oggetto=italia, inizio=poco_fa())
        Delega.objects.create(persona=delegato_nazionale_no_6, tipo=RESPONSABILE_AREA, oggetto=italia, inizio=poco_fa())
        Delega.objects.create(persona=delegato_toscana, tipo=DELEGATO_OBIETTIVO_6, oggetto=toscana, inizio=poco_fa())
        Delega.objects.create(persona=delegato_firenze, tipo=DELEGATO_OBIETTIVO_6, oggetto=firenze, inizio=poco_fa())
        Delega.objects.create(persona=delegato_firenze_no_5, tipo=DELEGATO_OBIETTIVO_5, oggetto=firenze, inizio=poco_fa())
        Delega.objects.create(persona=delegato_dicomano, tipo=DELEGATO_OBIETTIVO_6, oggetto=dicomano, inizio=poco_fa())
        Delega.objects.create(persona=delegato_empoli, tipo=DELEGATO_OBIETTIVO_6, oggetto=empoli, inizio=poco_fa())
        Delega.objects.create(persona=delegato_vinci, tipo=DELEGATO_OBIETTIVO_6, oggetto=vinci, inizio=poco_fa())
        Delega.objects.create(persona=delegato_abruzzo, tipo=DELEGATO_OBIETTIVO_3, oggetto=abruzzo, inizio=poco_fa())
        # Rubrica delegati obiettivo 6 per il delegato nazionale
        elenco = _rubrica_delegati(delegato_nazionale, DELEGATO_OBIETTIVO_6, sedi_tutte).risultati()
        self.assertEqual(5, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertIn(delegato_toscana, elenco)
        self.assertIn(delegato_firenze, elenco)
        self.assertIn(delegato_dicomano, elenco)
        self.assertIn(delegato_empoli, elenco)
        self.assertIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        # Rubrica delegati obiettivo 5 per il delegato nazionale
        elenco = _rubrica_delegati(delegato_nazionale, DELEGATO_OBIETTIVO_5, sedi_tutte)
        modulo_riempito = ModuloElencoVolontari({
            'includi_estesi': ModuloElencoVolontari.SI
        })
        elenco.modulo_riempito = modulo_riempito
        elenco = elenco.risultati()
        self.assertEqual(1, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato regionale toscana
        elenco = _rubrica_delegati(delegato_toscana, DELEGATO_OBIETTIVO_6, sedi_toscana).risultati()
        self.assertEqual(4, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertIn(delegato_firenze, elenco)
        self.assertIn(delegato_dicomano, elenco)
        self.assertIn(delegato_empoli, elenco)
        self.assertIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato provinciale firenze
        elenco = _rubrica_delegati(delegato_firenze, DELEGATO_OBIETTIVO_6, sedi_firenze).risultati()
        self.assertEqual(1, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato provinciale firenze, con sede filtrata
        elenco = _rubrica_delegati(delegato_firenze, DELEGATO_OBIETTIVO_6, sede_firenze).risultati()
        self.assertEqual(0, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato locale
        elenco = _rubrica_delegati(delegato_empoli, DELEGATO_OBIETTIVO_6, sedi_empoli).risultati()
        self.assertEqual(1, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato territoriale
        elenco = _rubrica_delegati(delegato_dicomano, DELEGATO_OBIETTIVO_6, sede_dicomano).risultati()
        self.assertEqual(0, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 6 per il delegato territoriale
        elenco = _rubrica_delegati(delegato_vinci, DELEGATO_OBIETTIVO_6, sede_vinci).risultati()
        self.assertEqual(0, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)
        # Rubrica delegati obiettivo 3 per il delegato regionale abruzzo
        elenco = _rubrica_delegati(delegato_abruzzo, DELEGATO_OBIETTIVO_3, sedi_abruzzo).risultati()
        self.assertEqual(0, len(elenco))
        self.assertNotIn(delegato_nazionale, elenco)
        self.assertNotIn(delegato_toscana, elenco)
        self.assertNotIn(delegato_firenze, elenco)
        self.assertNotIn(delegato_dicomano, elenco)
        self.assertNotIn(delegato_empoli, elenco)
        self.assertNotIn(delegato_vinci, elenco)
        self.assertNotIn(delegato_veneto, elenco)
        self.assertNotIn(delegato_emilia_romagna, elenco)
        self.assertNotIn(delegato_firenze_no_5, elenco)
        self.assertNotIn(delegato_nazionale_no_6, elenco)
        self.assertNotIn(delegato_abruzzo, elenco)

    def test_storico_richieste(self):

        presidente = crea_persona()
        crea_utenza(presidente, email=email_fittizzia())

        uff_soci, sede, __ = crea_persona_sede_appartenenza(presidente)
        Delega.objects.create(tipo=UFFICIO_SOCI, persona=uff_soci, oggetto=sede, firmatario=presidente, inizio=now())

        sede2 = crea_sede(presidente)
        self.assertEqual(presidente.deleghe.count(), 2)
        # Tutte le deleghe presidente partono da adesso per verificare il rispetto delle date
        # nello storico
        for delega in presidente.deleghe.all():
            delega.inizio = now()
            delega.save()

        socio = crea_persona()
        Appartenenza.objects.create(
            persona=socio, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO
        )

        trasf = Trasferimento.objects.create(
            destinazione=sede2,
            persona=socio,
            richiedente=socio,
            motivo='test'
        )
        trasf.richiedi()
        autorizzazione = Autorizzazione.objects.first()
        autorizzazione.concedi(
            firmatario=uff_soci,
            modulo=ModuloConsentiTrasferimento({'protocollo_numero': 1, 'protocollo_data': poco_fa()})
        )

        # L'autorizzazione chiesta dopo l'inizio della delega è visibile
        self.client.login(username=presidente.utenza.email, password='prova')
        response = self.client.get(reverse('autorizzazioni-storico'))
        self.assertContains(response, 'chiede il trasferimento verso')
        self.assertContains(response, sede2)
        self.assertContains(response, uff_soci.nome_completo)
        self.assertContains(response, socio.nome_completo)

        # L'autorizzazione chiesta prima dell'inizio della delega non è visibile
        autorizzazione.creazione = now() - datetime.timedelta(days=10)
        autorizzazione.save()
        response = self.client.get(reverse('autorizzazioni-storico'))
        self.assertNotContains(response, 'chiede il trasferimento verso')
        self.assertNotContains(response, sede2)
        self.assertNotContains(response, uff_soci.nome_completo)
        self.assertNotContains(response, socio.nome_completo)

        # Anticipando l'inizio della delega nell'altra sede la richiesta non è comunque visibile
        delega = presidente.deleghe.last()
        delega.inizio = now() - datetime.timedelta(days=20)
        delega.save()
        response = self.client.get(reverse('autorizzazioni-storico'))
        self.assertNotContains(response, 'chiede il trasferimento verso')
        self.assertNotContains(response, sede2)
        self.assertNotContains(response, uff_soci.nome_completo)
        self.assertNotContains(response, socio.nome_completo)

        # Anticipando l'inizio della delega nella sede corretta la richiesta è visibile
        delega = presidente.deleghe.first()
        delega.inizio = now() - datetime.timedelta(days=20)
        delega.save()
        delega = presidente.deleghe.last()
        delega.inizio = now() - datetime.timedelta(days=5)
        delega.save()
        response = self.client.get(reverse('autorizzazioni-storico'))
        self.assertContains(response, 'chiede il trasferimento verso')
        self.assertContains(response, sede2)
        self.assertContains(response, uff_soci.nome_completo)
        self.assertContains(response, socio.nome_completo)


class TestFunzionaliAnagrafica(TestFunzionale):

    def test_sede_trasferimento(self):
        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)
        crea_utenza(persona, email=email_fittizzia())
        sede_2 = crea_sede(presidente=presidente)

        self.client.login(username=persona.utenza.email, password="prova")
        dati = {
            'destinazione': sede_2.pk,
            'motivo': 'test',
        }
        response = self.client.post('/utente/trasferimento/', data=dati)
        self.assertNotContains(response=response, text='Sei già appartenente a questa sede')
        self.assertEqual(Autorizzazione.objects.filter(richiedente=persona, concessa=None).count(), 1)
        Autorizzazione.objects.get(richiedente=persona, concessa=None).nega(presidente)

        Appartenenza.objects.create(
            persona=persona,
            sede=sede_2,
            membro=Appartenenza.ESTESO,
            inizio="1980-12-10",
        )
        response = self.client.post('/utente/trasferimento/', data=dati)
        self.assertNotContains(response=response, text='Sei già appartenente a questa sede')
        self.assertEqual(Autorizzazione.objects.filter(richiedente=persona, concessa=None).count(), 1)
        Autorizzazione.objects.get(richiedente=persona, concessa=None).nega(presidente)

        Appartenenza.objects.create(
            persona=persona,
            sede=sede_2,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
        )
        response = self.client.post('/utente/trasferimento/', data=dati)
        self.assertContains(response=response, text='Sei già appartenente a questa sede')
        self.assertEqual(Autorizzazione.objects.filter(richiedente=persona, concessa=None).count(), 0)

    def test_us_attivazione_credenziali(self):

        EMAIL_UTENZA = email_fittizzia()

        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sessione_presidente = self.sessione_utente(persona=presidente)

        sessione_presidente.visit("%s%s" % (self.live_server_url, persona.url_profilo_credenziali))
        sessione_presidente.fill('email', EMAIL_UTENZA)
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        self.assertTrue(
            Utenza.objects.filter(persona=persona).exists(),
            msg="L'utenza e' stata creata correttamente"
        )

        self.assertTrue(
            Utenza.objects.get(persona=persona).email == EMAIL_UTENZA,
            msg="L'email e' stata correttamente creata"
        )

        # Ottieni e-mail inviata
        msg = Messaggio.objects.filter(oggetto__icontains="credenziali",
                                       oggetti_destinatario__persona=persona)

        self.assertTrue(
            msg.exists(),
            msg="Email delle credenziali spedita"
        )

        corpo_msg = msg.first().corpo

        self.assertTrue(
            EMAIL_UTENZA in corpo_msg,
            msg="L'email contiene il nuovo indirizzo e-mail"
        )

        doc = html.document_fromstring(corpo_msg)
        nuova_pwd = doc.xpath("//*[@id='nuova-password']")[0].text.strip()

        utenza = persona.utenza
        utenza.password_testing = nuova_pwd  # Password per accesso

        # Prova accesso con nuova utenza.
        sessione_persona = self.sessione_utente(utente=utenza)

    def test_us_cambio_credenziali(self):

        VECCHIA_EMAIL = email_fittizzia()
        NUOVA_EMAIL = email_fittizzia()

        presidente = crea_persona()
        persona, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)
        utenza = crea_utenza(persona=persona, email=VECCHIA_EMAIL)

        sessione_presidente = self.sessione_utente(persona=presidente)
        sessione_presidente.visit("%s%s" % (self.live_server_url, persona.url_profilo_credenziali))
        sessione_presidente.fill('email', NUOVA_EMAIL)
        sessione_presidente.check('ok_1')
        sessione_presidente.check('ok_3')
        sessione_presidente.check('ok_4')
        sessione_presidente.find_by_xpath("//button[@type='submit']").first.click()

        # Ottieni e-mail inviata
        msg = Messaggio.objects.filter(oggetto__icontains="credenziali",
                                       oggetti_destinatario__persona=persona)

        self.assertTrue(
            msg.exists(),
            msg="Email di avviso con nuove credenziali inviata"
        )

        msg_body = msg.first().corpo

        self.assertTrue(
            VECCHIA_EMAIL in msg_body,
            msg="Il messaggio contiene la vecchia e-mail"
        )

        self.assertTrue(
            NUOVA_EMAIL in msg_body,
            msg="Il messaggio contiene la nuova e-mail"
        )

        utenza = persona.utenza
        utenza.refresh_from_db()

        self.assertTrue(
            utenza.email == NUOVA_EMAIL,
            msg="E-mail di accesso cambiata correttamente"
        )

        sessione_persona = self.sessione_utente(utente=utenza)
        self.assertTrue(
            True,
            msg="Login effettuato con nuove credenziali"
        )

    def test_presidente_recursetree(self):
        """
        Questo test controlla che la pagina /presidente
        funzioni correttamente nel caso particolare di due sottoalberi
        completamente separati, che causa problemi e non puo essere usata
        con {% recursetree %}.
        """

        presidente = crea_persona()

        # Struttura:
        # x
        # - y       presidenza
        # - - a
        # - - - b   (unita)
        # - c       presidenza
        # - - d     (unita)
        x = crea_sede()
        y = crea_sede(genitore=x)
        a = crea_sede(genitore=y, presidente=presidente)
        b = crea_sede(genitore=a, estensione=TERRITORIALE)
        c = crea_sede(genitore=x, presidente=presidente)
        d = crea_sede(genitore=c, estensione=TERRITORIALE)

        sessione = self.sessione_utente(persona=presidente)
        sessione.click_link_by_partial_text("Sedi")

        self.assertTrue(
            sessione.is_text_present(c.nome),
            msg="Pagina caricata correttamente"
        )

    def test_modifica_codice_fiscale(self):
        p1 = crea_persona()
        p1.codice_fiscale = 'RSSMRA45C12F2LRI'
        p1.save()
        p2 = crea_persona()
        vecchio_codice_fiscale = 'MRTNTN23M02D969P'
        data = {
            'nome': 'Mario',
            'cognome': 'Rossi',
            'data_nascita': '1970-1-1',
            'comune_nascita': 'Firenze',
            'provincia_nascita': 'fi',
            'stato_nascita': 'IT',
            'indirizzo_residenza': 'Via Ghibellina 1',
            'comune_residenza': 'Firenze',
            'provincia_residenza': 'fi',
            'stato_residenza': 'IT',
            'cap_residenza': '52100',
            'codice_fiscale': vecchio_codice_fiscale,
        }

        nuovo_codice_fiscale_maiuscolo = p1.codice_fiscale
        nuovo_codice_fiscale_minuscolo = p1.codice_fiscale.lower()
        modulo = ModuloProfiloModificaAnagrafica(data, instance=p2)
        self.assertEqual(modulo.is_valid(), True)
        data['codice_fiscale'] = nuovo_codice_fiscale_minuscolo
        modulo = ModuloProfiloModificaAnagrafica(data, instance=p2)
        self.assertEqual(modulo.is_valid(), False)
        self.assertEqual(modulo.errors, {'codice_fiscale': ['Persona con questo Codice Fiscale esiste già.']})
        data['codice_fiscale'] = nuovo_codice_fiscale_maiuscolo
        modulo = ModuloProfiloModificaAnagrafica(data, instance=p2)
        self.assertEqual(modulo.is_valid(), False)
        self.assertEqual(modulo.errors, {'codice_fiscale': ['Persona con questo Codice Fiscale esiste già.']})
        data['codice_fiscale'] = vecchio_codice_fiscale.lower()
        modulo = ModuloProfiloModificaAnagrafica(data, instance=p2)
        self.assertEqual(modulo.is_valid(), True)
        self.assertEqual(p2.codice_fiscale, vecchio_codice_fiscale)

    def test_modifica_email(self):
        EMAIL_UTENZA = email_fittizzia()
        EMAIL_NUOVA = email_fittizzia()

        persona = crea_persona()
        utenza = crea_utenza(persona, EMAIL_UTENZA)

        sessione = self.sessione_utente(persona=persona)
        sessione.click_link_by_partial_text("Contatti")

        sessione.is_text_present(EMAIL_UTENZA)
        sessione.fill('email', EMAIL_NUOVA)
        sessione.find_by_xpath("//button[@type='submit']").first.click()

        sessione.is_text_present('Conferma nuovo indirizzo email')
        sessione.is_text_present(EMAIL_NUOVA)

        email = mail.outbox[0]
        code_re = re.compile("/utente/contatti/\?code_m=([^']+)")
        code_text = code_re.findall(email.alternatives[0][0])[0]
        sessione.visit("%s%s?code_m=%s" % (self.live_server_url, persona.url_contatti, code_text))

        sessione.is_text_present('Nuovo indirizzo email confermato!')

        utenza.refresh_from_db()

        self.assertTrue(
            utenza.email == EMAIL_NUOVA,
            msg="E-mail di accesso cambiata correttamente"
        )

    def test_registrazione_non_valida(self):

        client = Client()
        response = client.get('/registrati/aspirante/anagrafica/?code=random_str')
        self.assertContains(response, 'Errore nel processo di registrazione.')

        response = client.get('/registrati/aspirante/anagrafica/?code=random_str&registration=random_session')
        self.assertContains(response, 'Errore nel processo di registrazione.')

    def test_rubriche_delegati(self):
        EMAIL = email_fittizzia()
        italia = crea_sede(estensione=NAZIONALE)
        toscana = crea_sede(estensione=REGIONALE, genitore=italia)
        veneto = crea_sede(estensione=REGIONALE, genitore=italia)
        abruzzo = crea_sede(estensione=REGIONALE, genitore=italia)
        emilia_romagna = crea_sede(estensione=REGIONALE, genitore=italia)
        firenze = crea_sede(estensione=LOCALE, genitore=toscana)
        dicomano = crea_sede(estensione=TERRITORIALE, genitore=firenze)
        empoli = crea_sede(estensione=LOCALE, genitore=toscana)
        territorio_empoli = crea_sede(estensione=TERRITORIALE, genitore=empoli)
        delegato_nazionale = crea_persona()
        delegato_nazionale_no_6 = crea_persona()
        delegato_toscana = crea_persona()
        delegato_firenze = crea_persona()
        delegato_firenze_no_6 = crea_persona()
        delegato_dicomano = crea_persona()
        delegato_empoli = crea_persona()
        delegato_territorio_empoli = crea_persona()
        delegato_veneto = crea_persona()
        delegato_emilia_romagna = crea_persona()
        delegato_abruzzo = crea_persona()
        Delega.objects.create(persona=delegato_nazionale, tipo=DELEGATO_OBIETTIVO_6, oggetto=italia, inizio=poco_fa())
        Delega.objects.create(persona=delegato_nazionale_no_6, tipo=RESPONSABILE_AREA, oggetto=italia, inizio=poco_fa())
        Delega.objects.create(persona=delegato_toscana, tipo=DELEGATO_OBIETTIVO_6, oggetto=toscana, inizio=poco_fa())
        Delega.objects.create(persona=delegato_firenze, tipo=DELEGATO_OBIETTIVO_6, oggetto=firenze, inizio=poco_fa())
        Delega.objects.create(persona=delegato_firenze_no_6, tipo=DELEGATO_OBIETTIVO_5, oggetto=firenze, inizio=poco_fa())
        Delega.objects.create(persona=delegato_dicomano, tipo=DELEGATO_OBIETTIVO_6, oggetto=dicomano, inizio=poco_fa())
        Delega.objects.create(persona=delegato_empoli, tipo=DELEGATO_OBIETTIVO_6, oggetto=empoli, inizio=poco_fa())
        Delega.objects.create(persona=delegato_territorio_empoli, tipo=DELEGATO_OBIETTIVO_6, oggetto=territorio_empoli, inizio=poco_fa())
        Delega.objects.create(persona=delegato_abruzzo, tipo=DELEGATO_OBIETTIVO_3, oggetto=abruzzo, inizio=poco_fa())
        # Testa la rubrica per il delegato nazionale
        utenza = crea_utenza(persona=delegato_nazionale, email=EMAIL)
        sessione_delegato_nazionale = self.sessione_utente(utente=utenza, wait_time=1)
        sessione_delegato_nazionale.visit("%s%s" % (self.live_server_url, '/utente/'))
        self.assertTrue(sessione_delegato_nazionale.is_text_present("Rubrica"))
        self.assertTrue(sessione_delegato_nazionale.is_text_present("Referenti"))
        self.assertTrue(sessione_delegato_nazionale.is_text_present("Volontari"))
        self.assertTrue(sessione_delegato_nazionale.is_text_present("Delegati Obiettivo VI (Sviluppo)"))
        sessione_delegato_nazionale.click_link_by_partial_href('delegati_obiettivo_6')
        sessione_delegato_nazionale.find_by_css('.col-md-3 .btn-primary').first.click()
        with sessione_delegato_nazionale.get_iframe(0) as iframe:
            self.assertTrue(iframe.is_text_present(delegato_toscana.nome))
            self.assertTrue(iframe.is_text_present(delegato_firenze.nome))
            self.assertTrue(iframe.is_text_present(delegato_empoli.nome))
            self.assertTrue(iframe.is_text_present(delegato_dicomano.nome))
            self.assertTrue(iframe.is_text_present(delegato_territorio_empoli.nome))
            self.assertFalse(iframe.is_text_present(delegato_nazionale.nome))
            self.assertTrue(iframe.is_text_present(delegato_toscana.cognome))
            self.assertTrue(iframe.is_text_present(delegato_firenze.cognome))
            self.assertTrue(iframe.is_text_present(firenze.nome_completo))
            self.assertTrue(iframe.is_text_present(delegato_empoli.cognome))
            self.assertTrue(iframe.is_text_present(delegato_dicomano.cognome))
            self.assertTrue(iframe.is_text_present(delegato_territorio_empoli.cognome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.nome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.cognome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.nome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.cognome))
        sessione_delegato_nazionale.click_link_by_partial_href('delegati_obiettivo_6')
        for sede in  sessione_delegato_nazionale.find_by_name('sedi'):
            if int(sede.value) == firenze.pk:
                sede.check()
            else:
                sede.uncheck()
        sessione_delegato_nazionale.find_by_css('.col-md-3 .btn-primary').first.click()
        with sessione_delegato_nazionale.get_iframe(0) as iframe:
            self.assertFalse(iframe.is_text_present(delegato_nazionale.nome))
            self.assertFalse(iframe.is_text_present(delegato_toscana.nome))
            self.assertTrue(iframe.is_text_present(delegato_firenze.nome))
            self.assertFalse(iframe.is_text_present(delegato_empoli.nome))
            self.assertFalse(iframe.is_text_present(delegato_dicomano.nome))
            self.assertFalse(iframe.is_text_present(delegato_territorio_empoli.nome))
            self.assertFalse(iframe.is_text_present(delegato_nazionale.nome))
            self.assertFalse(iframe.is_text_present(delegato_toscana.cognome))
            self.assertTrue(iframe.is_text_present(delegato_firenze.cognome))
            self.assertFalse(iframe.is_text_present(delegato_empoli.cognome))
            self.assertFalse(iframe.is_text_present(delegato_dicomano.cognome))
            self.assertFalse(iframe.is_text_present(delegato_territorio_empoli.cognome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.nome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.cognome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.nome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.cognome))

        # Testa la rubrica per il delegato di firenze
        EMAIL = email_fittizzia()
        utenza = crea_utenza(persona=delegato_firenze, email=EMAIL)
        sessione_delegato_firenze = self.sessione_utente(utente=utenza, wait_time=1)
        sessione_delegato_firenze.visit("%s%s" % (self.live_server_url, '/utente/'))
        self.assertTrue(sessione_delegato_firenze.is_text_present("Rubrica"))
        self.assertTrue(sessione_delegato_firenze.is_text_present("Referenti"))
        self.assertTrue(sessione_delegato_firenze.is_text_present("Volontari"))
        self.assertTrue(sessione_delegato_firenze.is_text_present("Delegati Obiettivo VI (Sviluppo)"))
        sessione_delegato_firenze.click_link_by_partial_href('delegati_obiettivo_6')
        sessione_delegato_firenze.find_by_css('.col-md-3 .btn-primary').first.click()
        with sessione_delegato_firenze.get_iframe(0) as iframe:
            self.assertFalse(iframe.is_text_present(delegato_nazionale.nome))
            self.assertFalse(iframe.is_text_present(delegato_toscana.nome))
            self.assertFalse(iframe.is_text_present(delegato_firenze.nome))
            self.assertFalse(iframe.is_text_present(delegato_empoli.nome))
            self.assertTrue(iframe.is_text_present(delegato_dicomano.nome))
            self.assertFalse(iframe.is_text_present(delegato_territorio_empoli.nome))
            self.assertFalse(iframe.is_text_present(delegato_nazionale.nome))
            self.assertFalse(iframe.is_text_present(delegato_toscana.cognome))
            self.assertFalse(iframe.is_text_present(delegato_firenze.cognome))
            self.assertFalse(iframe.is_text_present(delegato_empoli.cognome))
            self.assertTrue(iframe.is_text_present(delegato_dicomano.cognome))
            self.assertFalse(iframe.is_text_present(delegato_territorio_empoli.cognome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.nome))
            self.assertFalse(iframe.is_text_present(delegato_firenze_no_6.cognome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.nome))
            self.assertFalse(iframe.is_text_present(delegato_veneto.cognome))
        # Testa la rubrica per il delegato territoriale dicomano
        EMAIL = email_fittizzia()
        utenza = crea_utenza(persona=delegato_dicomano, email=EMAIL)
        sessione_delegato_dicomano = self.sessione_utente(utente=utenza, wait_time=1)
        sessione_delegato_dicomano.visit("%s%s" % (self.live_server_url, '/utente/'))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Rubrica"))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Referenti"))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Volontari"))
        self.assertFalse(sessione_delegato_dicomano.is_text_present("Delegati Obiettivo VI (Sviluppo)"))
        # Testa la rubrica per il delegato regionale abruzzo (non vede la rubrica)
        EMAIL = email_fittizzia()
        utenza = crea_utenza(persona=delegato_abruzzo, email=EMAIL)
        sessione_delegato_abruzzo = self.sessione_utente(utente=utenza, wait_time=1)
        sessione_delegato_abruzzo.visit("%s%s" % (self.live_server_url, '/utente/'))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Rubrica"))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Referenti"))
        self.assertTrue(sessione_delegato_dicomano.is_text_present("Volontari"))
        self.assertFalse(sessione_delegato_dicomano.is_text_present("Delegati Obiettivo III (Emergenze)"))
