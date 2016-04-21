from django.test import TestCase

# Create your tests here.

import datetime

from django.test import TestCase
from lxml import html

from anagrafica.costanti import LOCALE, PROVINCIALE, REGIONALE, NAZIONALE, TERRITORIALE
from anagrafica.forms import ModuloCreazioneEstensione, ModuloNegaEstensione
from anagrafica.models import Sede, Persona, Appartenenza, Documento, Delega
from anagrafica.permessi.applicazioni import RESPONSABILE_AUTOPARCO, UFFICIO_SOCI, PRESIDENTE, UFFICIO_SOCI_UNITA
from anagrafica.permessi.costanti import MODIFICA, ELENCHI_SOCI, LETTURA, GESTIONE_SOCI
from autenticazione.models import Utenza
from autenticazione.utils_test import TestFunzionale
from base.models import Autorizzazione
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, email_fittizzia, \
    crea_utenza
from posta.models import Messaggio
from .models import NotiziaTest, NotiziaTestSegmento



class TestSegmenti(TestCase):

    def test_appartenenza(self):

        # Notizie di test
        notizia_1 = NotiziaTest.objects.create(testo="Notizia 1: Testo di prova!")
        notizia_2 = NotiziaTest.objects.create(testo="Notizia 2: Altro testo di prova!")

        # SEGMENTI NOTIZIA_1
        # Segmento per filtrare tutti gli utenti
        segmento_tutti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='A',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i volontari
        segmento_volontari_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='B',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_meno_35_anni_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='E',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_35_anni_o_piu_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='F',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i sostenitori
        segmento_sostenitori_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='G',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i presidenti con delega attiva
        segmento_presidenti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='I',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i delegati Ufficio Soci con delega attiva
        segmento_delegati_US_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='L',
            notizia=notizia_1
        )
        # Segmento per filtrare tutti i delegati Autoparco con delega attiva
        segmento_delegati_autoparco_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='Y',
            notizia=notizia_1
        )


        # Utente gaia generico
        persona = crea_persona()
        persona.save()

        # Test appartenenza
        esito = persona.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = persona.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = persona.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Volontario
        volontario = crea_persona()
        volontario.save()

        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        c2 = crea_sede(estensione=TERRITORIALE, genitore=c)
        c2.save()

        a = Appartenenza(
            persona=volontario,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        esito = volontario.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Volontario con meno di 35 anni
        volontario_meno_35_anni = crea_persona()
        volontario_meno_35_anni.save()

        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        c2 = crea_sede(estensione=TERRITORIALE, genitore=c)
        c2.save()

        a = Appartenenza(
            persona=volontario_meno_35_anni,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_volontari_meno_35_anni_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Volontario con 35 anni o più di età
        volontario_35_anni_o_piu = crea_persona()
        volontario_35_anni_o_piu.data_nascita = "1960-2-5"
        volontario_35_anni_o_piu.save()

        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        c2 = crea_sede(estensione=TERRITORIALE, genitore=c)
        c2.save()

        a = Appartenenza(
            persona=volontario_35_anni_o_piu,
            sede=c,
            membro=Appartenenza.VOLONTARIO,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        esito = volontario_35_anni_o_piu.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_35_anni_o_piu.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_35_anni_o_piu.appartiene_al_segmento(segmento_volontari_meno_35_anni_no_filtri)
        self.assertFalse(esito)
        esito = volontario_35_anni_o_piu.appartiene_al_segmento(segmento_volontari_35_anni_o_piu_no_filtri)
        self.assertTrue(esito)
        esito = volontario_35_anni_o_piu.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Sostenitore
        sostenitore = crea_persona()
        sostenitore.save()

        c = crea_sede(estensione=PROVINCIALE)
        c.save()

        c2 = crea_sede(estensione=TERRITORIALE, genitore=c)
        c2.save()

        a = Appartenenza(
            persona=sostenitore,
            sede=c,
            membro=Appartenenza.SOSTENITORE,
            inizio="1980-12-10",
            confermata=True
        )
        a.save()

        esito = sostenitore.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = sostenitore.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = sostenitore.appartiene_al_segmento(segmento_sostenitori_no_filtri)
        self.assertTrue(esito)
        esito = sostenitore.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Presidente
        presidente = crea_persona()
        presidente.save()

        # Delega scaduta
        delega_presidente_scaduta = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=c,
            inizio="2000-12-10",
            fine="2010-12-10"
        )
        delega_presidente_scaduta.save()

        esito = presidente.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = presidente.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = presidente.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Delega futura
        delega_presidente_futura = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=c,
            inizio=datetime.datetime.now() + datetime.timedelta(days=1),
            fine="2050-12-10"
        )
        delega_presidente_futura.save()
        esito = presidente.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Delega in corso
        delega_presidente_in_corso = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=c,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_in_corso.save()
        esito = presidente.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertTrue(esito)

        # Delegato Ufficio Soci
        delegato_US = crea_persona()
        delegato_US.save()

        delega_ufficio_soci = Delega(
            persona=delegato_US,
            tipo=UFFICIO_SOCI,
            oggetto=c,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_ufficio_soci.save()

        esito = delegato_US.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertTrue(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertFalse(esito)

        # Delegato Autoparco
        delegato_autoparco = crea_persona()
        delegato_autoparco.save()

        delega_autoparco = Delega(
            persona=delegato_autoparco,
            tipo=RESPONSABILE_AUTOPARCO,
            oggetto=c,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_autoparco.save()

        esito = delegato_autoparco.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertFalse(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertTrue(esito)
