import datetime

from django.test import TestCase

from anagrafica.costanti import REGIONALE
from anagrafica.models import Appartenenza, Delega
from anagrafica.permessi.applicazioni import (DELEGATO_OBIETTIVO_1,
                                              DELEGATO_OBIETTIVO_2,
                                              DELEGATO_OBIETTIVO_3,
                                              DELEGATO_OBIETTIVO_4,
                                              DELEGATO_OBIETTIVO_5,
                                              DELEGATO_OBIETTIVO_6, PRESIDENTE,
                                              REFERENTE,
                                              RESPONSABILE_AUTOPARCO,
                                              RESPONSABILE_FORMAZIONE,
                                              UFFICIO_SOCI)
from attivita.models import Area, Attivita
from base.utils import poco_fa
from base.utils_tests import (crea_appartenenza, crea_persona,
                              crea_persona_sede_appartenenza, crea_sede,
                              crea_utenza, crea_area_attivita)
from curriculum.models import Titolo, TitoloPersonale
from formazione.models import Aspirante, CorsoBase, PartecipazioneCorsoBase

from .models import NotiziaTest, NotiziaTestSegmento


class TestSegmenti(TestCase):

    def test_appartenenza(self):

        data_corrente = datetime.date.today()
        anno_corrente = data_corrente.year

        LIVELLI_DELEGATI = [(DELEGATO_OBIETTIVO_1, 'M'), (DELEGATO_OBIETTIVO_2, 'N'), (DELEGATO_OBIETTIVO_3, 'O'), (DELEGATO_OBIETTIVO_4, 'P'), (DELEGATO_OBIETTIVO_5, 'Q'), (DELEGATO_OBIETTIVO_6, 'R')]
        LIVELLI_ATTIVITA = ['S', 'T', 'U', 'V', 'W', 'X']

        # Notizie di test
        notizia_1 = NotiziaTest.objects.create(testo="Notizia 1: Testo di prova!")
        notizia_2 = NotiziaTest.objects.create(testo="Notizia 2: Altro testo di prova!")

        # SEGMENTI NOTIZIA_1
        # Segmento per filtrare tutti gli utenti
        segmento_tutti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='A',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari
        segmento_volontari_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='B',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di un anno di attivita
        segmento_volontari_meno_uno_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='C',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con più di un anno di attivita
        segmento_volontari_piu_uno_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='D',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_meno_35_anni_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='E',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_35_anni_o_piu_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='F',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i sostenitori
        segmento_sostenitori_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='G',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i sostenitori
        segmento_aspiranti_corsisti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='H',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti con delega attiva
        segmento_presidenti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='I',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti di comitati locali con delega attiva
        segmento_presidenti_comitati_locali_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='J',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti di comitati regionali con delega attiva
        segmento_presidenti_comitati_regionali_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='K',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Ufficio Soci con delega attiva
        segmento_delegati_US_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='L',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Autoparco con delega attiva
        segmento_delegati_autoparco_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='Y',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Formazione con delega attiva
        segmento_delegati_formazione_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='Z',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con titolo
        titolo_patenteCRI = Titolo.objects.create(tipo='PC', nome='Titolo test')
        segmento_volontari_con_titolo_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='AA',
            notiziatest=notizia_1,
            titolo=titolo_patenteCRI
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
        volontario, _, _ = crea_persona_sede_appartenenza()

        esito = volontario.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Volontario con meno di un anno di attività
        volontario_meno_uno, _, _ = crea_persona_sede_appartenenza()
        volontario_meno_uno.creazione = data_corrente - datetime.timedelta(days=5)
        volontario_meno_uno.save()
        esito = volontario_meno_uno.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_uno.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_uno.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        # TODO: creare dati di test per verificare il segmento
        #esito = volontario_meno_uno.appartiene_al_segmento(segmento_volontari_piu_uno_no_filtri)
        #self.assertFalse(esito)
        #esito = volontario_meno_uno.appartiene_al_segmento(segmento_volontari_meno_uno_no_filtri)
        #self.assertTrue(esito)

        # Volontario con più di un anno di attività
        volontario_piu_uno, _, _ = crea_persona_sede_appartenenza()
        volontario_piu_uno.creazione = data_corrente - datetime.timedelta(days=720)
        volontario_piu_uno.save()
        esito = volontario_piu_uno.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_piu_uno.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_piu_uno.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        # TODO: creare dati di test per verificare il segmento
        #esito = volontario_piu_uno.appartiene_al_segmento(segmento_volontari_meno_uno_no_filtri)
        #self.assertFalse(esito)
        #esito = volontario_piu_uno.appartiene_al_segmento(segmento_volontari_piu_uno_no_filtri)
        #self.assertTrue(esito)

        # Volontario con meno di 35 anni
        volontario_meno_35_anni, _, _ = crea_persona_sede_appartenenza()

        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_volontari_meno_35_anni_no_filtri)
        self.assertTrue(esito)
        esito = volontario_meno_35_anni.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)

        # Volontario con 35 anni o più di età
        volontario_35_anni_o_piu, _, _ = crea_persona_sede_appartenenza()
        volontario_35_anni_o_piu.data_nascita = "1960-2-5"
        volontario_35_anni_o_piu.save()

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
        sostenitore, _, appartenenza = crea_persona_sede_appartenenza()
        appartenenza.membro = Appartenenza.SOSTENITORE
        appartenenza.save()

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
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)
        delega_presidente_in_corso = Delega(
            persona=presidente,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_in_corso.save()
        esito = presidente.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = presidente.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = presidente.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertTrue(esito)

        # Presidente comitato locale
        presidente_comitato_locale = crea_persona()

        presidente_comitato_locale, sede, appartenenza = crea_persona_sede_appartenenza(presidente_comitato_locale)
        delega_presidente_comitato_locale_in_corso = Delega(
            persona=presidente_comitato_locale,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_comitato_locale_in_corso.save()

        esito = presidente_comitato_locale.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_locale.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_locale.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_locale.appartiene_al_segmento(segmento_presidenti_comitati_locali_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_locale.appartiene_al_segmento(segmento_presidenti_comitati_regionali_no_filtri)
        self.assertFalse(esito)

        # Presidente comitato regionale
        presidente_comitato_regionale = crea_persona()

        presidente_comitato_regionale, sede, appartenenza = crea_persona_sede_appartenenza(presidente_comitato_regionale)
        sede.estensione = REGIONALE
        sede.save()
        delega_presidente_comitato_regionale_in_corso = Delega(
            persona=presidente_comitato_regionale,
            tipo=PRESIDENTE,
            oggetto=sede,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_presidente_comitato_regionale_in_corso.save()

        esito = presidente_comitato_regionale.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_regionale.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_regionale.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertTrue(esito)
        esito = presidente_comitato_regionale.appartiene_al_segmento(segmento_presidenti_comitati_locali_no_filtri)
        self.assertFalse(esito)
        esito = presidente_comitato_regionale.appartiene_al_segmento(segmento_presidenti_comitati_regionali_no_filtri)
        self.assertTrue(esito)

        # Delegato Ufficio Soci
        delegato_US = crea_persona()
        sede_delegato_US = crea_sede()
        appartenenza = crea_appartenenza(delegato_US, sede_delegato_US)

        delega_ufficio_soci = Delega(
            persona=delegato_US,
            tipo=UFFICIO_SOCI,
            oggetto=sede_delegato_US,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_ufficio_soci.save()

        esito = delegato_US.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertTrue(esito)
        esito = delegato_US.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertFalse(esito)

        # Delegati Obiettivo

        for livello_obiettivo in LIVELLI_DELEGATI:
            delegato = crea_persona()
            sede_delegato = crea_sede()
            appartenenza = crea_appartenenza(delegato, sede_delegato)
            segmento = NotiziaTestSegmento.objects.create(
                segmento=livello_obiettivo[1],
                notiziatest=notizia_1
            )
            delega_obiettivo = Delega(
                persona=delegato,
                tipo=livello_obiettivo[0],
                oggetto=sede_delegato,
                inizio=datetime.datetime.now() - datetime.timedelta(days=5),
                fine=datetime.datetime.now() + datetime.timedelta(days=5)
            )
            delega_obiettivo.save()

            esito = delegato.appartiene_al_segmento(segmento_tutti_no_filtri)
            self.assertTrue(esito)
            esito = delegato.appartiene_al_segmento(segmento_volontari_no_filtri)
            self.assertTrue(esito)
            esito = delegato.appartiene_al_segmento(segmento_presidenti_no_filtri)
            self.assertFalse(esito)
            esito = delegato.appartiene_al_segmento(segmento)
            self.assertTrue(esito)
            esito = delegato.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
            self.assertFalse(esito)

        # Referenti attività area
        for idx, livello_attivita in enumerate(LIVELLI_ATTIVITA):
            referente = crea_persona()
            sede_referente = crea_sede()
            appartenenza = crea_appartenenza(referente, sede_referente)
            segmento = NotiziaTestSegmento.objects.create(
                segmento=livello_attivita,
                notiziatest=notizia_1
            )
            delega_referente = Delega(
                persona=referente,
                tipo=REFERENTE,
                oggetto=sede_referente,
                inizio=datetime.datetime.now() - datetime.timedelta(days=5),
                fine=datetime.datetime.now() + datetime.timedelta(days=5)
            )
            delega_referente.save()
            area, attivita = crea_area_attivita(sede=sede_referente)
            area.obiettivo = idx + 1
            area.save()
            attivita.aggiungi_delegato(REFERENTE, referente)
            esito = referente.appartiene_al_segmento(segmento_tutti_no_filtri)
            self.assertTrue(esito)
            esito = referente.appartiene_al_segmento(segmento_volontari_no_filtri)
            self.assertTrue(esito)
            esito = referente.appartiene_al_segmento(segmento_presidenti_no_filtri)
            self.assertFalse(esito)
            esito = referente.appartiene_al_segmento(segmento)
            self.assertTrue(esito)
            esito = referente.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
            self.assertFalse(esito)

        # Delegato Autoparco
        delegato_autoparco = crea_persona()
        sede_delegato_autoparco = crea_sede()
        appartenenza = crea_appartenenza(delegato_autoparco, sede_delegato_autoparco)

        delega_autoparco = Delega(
            persona=delegato_autoparco,
            tipo=RESPONSABILE_AUTOPARCO,
            oggetto=sede_delegato_autoparco,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_autoparco.save()

        esito = delegato_autoparco.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertFalse(esito)
        esito = delegato_autoparco.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertTrue(esito)

        # Delegato Formazione
        delegato_formazione = crea_persona()
        sede_delegato_formazione = crea_sede()
        appartenenza = crea_appartenenza(delegato_formazione, sede_delegato_formazione)

        delega_formazione = Delega(
            persona=delegato_formazione,
            tipo=RESPONSABILE_FORMAZIONE,
            oggetto=sede_delegato_formazione,
            inizio=datetime.datetime.now() - datetime.timedelta(days=5),
            fine=datetime.datetime.now() + datetime.timedelta(days=5)
        )
        delega_formazione.save()

        esito = delegato_formazione.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = delegato_formazione.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = delegato_formazione.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = delegato_formazione.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertFalse(esito)
        esito = delegato_formazione.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertFalse(esito)
        esito = delegato_formazione.appartiene_al_segmento(segmento_delegati_formazione_no_filtri)
        self.assertTrue(esito)

        # Aspirante volontario iscritto ad un corso
        aspirante_corsista = crea_persona()
        sede = crea_sede()
        aspirante = Aspirante(persona=aspirante_corsista)
        aspirante.save()
        corso = CorsoBase.objects.create(
            stato='A',
            sede=sede,
            data_inizio=datetime.datetime.now() + datetime.timedelta(days=5),
            data_esame=datetime.datetime.now() + datetime.timedelta(days=25),
            progressivo=1,
            anno=anno_corrente
        )
        partecipazione = PartecipazioneCorsoBase(
            persona=aspirante_corsista,
            corso=corso
        )
        partecipazione.ammissione = 'AM'
        partecipazione.save()

        esito = aspirante_corsista.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertFalse(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_delegati_US_no_filtri)
        self.assertFalse(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_delegati_autoparco_no_filtri)
        self.assertFalse(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_delegati_formazione_no_filtri)
        self.assertFalse(esito)
        esito = aspirante_corsista.appartiene_al_segmento(segmento_aspiranti_corsisti_no_filtri)
        self.assertTrue(esito)

        # Volontario con titolo
        volontario_con_titolo, _, _ = crea_persona_sede_appartenenza()
        titolo_personale = TitoloPersonale.objects.create(titolo=titolo_patenteCRI, persona=volontario_con_titolo)
        esito = volontario_con_titolo.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_con_titolo.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_con_titolo.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito =volontario_con_titolo.appartiene_al_segmento(segmento_volontari_con_titolo_no_filtri)
        self.assertTrue(esito)

        # Volontario con titolo di tipo differente dal filtro
        volontario_con_titolo_differente, _, _ = crea_persona_sede_appartenenza()
        titolo_patenteCIVILE = Titolo.objects.create(tipo='PP', nome='Titolo test 2')
        titolo_personale = TitoloPersonale.objects.create(titolo=titolo_patenteCIVILE, persona=volontario_con_titolo_differente)
        esito = volontario_con_titolo_differente.appartiene_al_segmento(segmento_tutti_no_filtri)
        self.assertTrue(esito)
        esito = volontario_con_titolo_differente.appartiene_al_segmento(segmento_volontari_no_filtri)
        self.assertTrue(esito)
        esito = volontario_con_titolo_differente.appartiene_al_segmento(segmento_presidenti_no_filtri)
        self.assertFalse(esito)
        esito = volontario_con_titolo_differente.appartiene_al_segmento(segmento_volontari_con_titolo_no_filtri)
        self.assertFalse(esito)


class TestSegmentiUtente(TestCase):

    def test_list_segmenti(self):
        volontario_con_titolo, _, _ = crea_persona_sede_appartenenza()

        # Notizie di test
        notizia_1 = NotiziaTest.objects.create(testo="Notizia 1: Testo di prova!")
        notizia_2 = NotiziaTest.objects.create(testo="Notizia 2: Altro testo di prova!")

        # SEGMENTI NOTIZIA_1
        # Segmento per filtrare tutti gli utenti
        segmento_tutti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='A',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari
        segmento_volontari_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='B',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di un anno di attivita
        segmento_volontari_meno_uno_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='C',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con più di un anno di attivita
        segmento_volontari_piu_uno_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='D',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_meno_35_anni_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='E',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con meno di 35 anni
        segmento_volontari_35_anni_o_piu_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='F',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i sostenitori
        segmento_sostenitori_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='G',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i sostenitori
        segmento_aspiranti_corsisti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='H',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti con delega attiva
        segmento_presidenti_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='I',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti di comitati locali con delega attiva
        segmento_presidenti_comitati_locali_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='J',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i presidenti di comitati regionali con delega attiva
        segmento_presidenti_comitati_regionali_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='K',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Ufficio Soci con delega attiva
        segmento_delegati_US_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='L',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Autoparco con delega attiva
        segmento_delegati_autoparco_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='Y',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i delegati Formazione con delega attiva
        segmento_delegati_formazione_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='Z',
            notiziatest=notizia_1
        )
        # Segmento per filtrare tutti i volontari con titolo
        titolo_patenteCRI = Titolo.objects.create(tipo='PC', nome='Titolo test')
        segmento_volontari_con_titolo_no_filtri = NotiziaTestSegmento.objects.create(
            segmento='AA',
            notiziatest=notizia_1,
            titolo=titolo_patenteCRI
        )

        qs = NotiziaTestSegmento.objects.all()
        risultato = qs.filtra_per_segmenti(volontario_con_titolo)
        attesi = [
            segmento_tutti_no_filtri, segmento_volontari_no_filtri,
            segmento_volontari_meno_uno_no_filtri, segmento_volontari_meno_35_anni_no_filtri
        ]
        self.assertEqual(set(risultato), set(attesi))