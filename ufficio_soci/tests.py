import datetime
from unittest import skip
import tempfile

import django.core.files
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from anagrafica.costanti import NAZIONALE, PROVINCIALE, REGIONALE
from anagrafica.models import Appartenenza, Sede, Persona, Fototessera, Dimissione
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from autenticazione.utils_test import TestFunzionale
from base.geo import Locazione
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, \
    crea_utenza, crea_locazione, email_fittizzia
from ufficio_soci.elenchi import ElencoElettoratoAlGiorno, ElencoSociAlGiorno, ElencoSostenitori, ElencoExSostenitori
from ufficio_soci.forms import ModuloElencoElettorato, ModuloReclamaQuota
from ufficio_soci.models import Tesseramento, Tesserino, Quota, Riduzione


class TestBase(TestCase):

    def setUp(self):
        self.p, self.s, self.a = crea_persona_sede_appartenenza()
        self.oggi = datetime.date(2015, 1, 1)
        self.quindici_anni_fa = (datetime.date(2000, 1, 1))
        self.venti_anni_fa = (datetime.date(1995, 1, 1))
        self.due_anni_e_mezo_fa = datetime.date(2012, 6, 15)
        self.un_anno_fa = datetime.date(2014, 1, 1)
        self.un_anno_e_mezzo_fa = datetime.date(2013, 6, 15)
        self.sei_mesi_fa = datetime.date(2015, 6, 1)
        self.nove_mesi_fa = datetime.date(2015, 3, 1)

        def _elettorato(tipo="attivo"):
            if tipo not in ("attivo", "passivo",):
                raise ValueError("Usa 'attivo' o 'passivo")

            if tipo == "attivo":
                tipo = ModuloElencoElettorato.ELETTORATO_ATTIVO
            else:
                tipo = ModuloElencoElettorato.ELETTORATO_PASSIVO

            modulo_riempito = ModuloElencoElettorato({
                "elettorato": tipo,
                "al_giorno": self.oggi.strftime("%Y-%m-%d")
            })
            if not modulo_riempito.is_valid():
                raise ValueError("Modulo non valido (inaspettatamente)")
            qs_sedi = Sede.objects.filter(pk__in=[self.s.pk])

            elenco = ElencoElettoratoAlGiorno(qs_sedi)
            elenco.modulo_riempito = modulo_riempito
            return elenco.risultati()

        def _elettorato_contiene(tipo="attivo", persona=None):
            if not isinstance(persona, Persona):
                raise ValueError("Persona passata non e' di tipo Persona.")
            el = _elettorato(tipo)
            r = el.filter(pk=persona.pk)
            return r.exists()

        self._elettorato = _elettorato
        self._elettorato_contiene = _elettorato_contiene

    def test_elettorato_attivo_unica_appartenenza(self):
        """
        Unica appartenenza
        """

        self.p.data_nascita = self.venti_anni_fa
        self.p.save()

        self.a.inizio = "2013-01-01"  # 2 anni fa
        self.a.fine = None
        self.a.membro = Appartenenza.VOLONTARIO
        self.a.save()

        self.assertTrue(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo contiene volontari con unica appartenenza valida"
        )

    def test_elettorato_passivo_unica_appartenenza(self):
        self.assertTrue(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato passivo contiene volontari con unica appartenenza valida",
        )

    def test_elettorato_minorenni_esclusi_da_elettorato_passivo(self):
        self.p.data_nascita = self.quindici_anni_fa
        self.p.save()

        self.assertTrue(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo contiene minorenni"
        )
        self.assertFalse(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato passivo non contiene minorenni"
        )

    def test_elettorato_attivo_singola_appartenenza_anzianita_non_soddisfatta(self):
        self.p.data_nascita = self.venti_anni_fa
        self.p.save()

        self.a.inizio = self.sei_mesi_fa
        self.a.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo richiede anzianita"
        )

    def test_elettorato_passivo_singola_appartenenza_anzianita_non_soddisfatta(self):

        self.p.data_nascita = self.venti_anni_fa
        self.p.save()

        self.a.inizio = self.un_anno_fa
        self.a.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato passivo richiede anzianita"
        )

    def test_elettorato_attivo_trasferimento_anzianita_soddisfatta(self):

        x = Appartenenza(
            persona=self.p,
            sede=self.s,
            inizio=self.due_anni_e_mezo_fa,
            fine=self.sei_mesi_fa,
            terminazione=Appartenenza.TRASFERIMENTO,
        )
        x.save()

        self.a.inizio = self.sei_mesi_fa
        self.a.fine = None
        self.a.precedente = x
        self.a.save()

        self.assertTrue(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo contiene volontari con doppia appartenenza valida (trasf.)"
        )

        x.inizio = self.nove_mesi_fa
        x.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo non contiene volontari con doppia appartenenza invalida (trasf.)"
        )

        self.a.precedente = None
        self.a.save()
        x.delete()

    def test_elettorato_passivo_dimissione_anzianita_soddisfatta(self):

        x = Appartenenza(
            persona=self.p,
            sede=self.s,
            inizio=self.due_anni_e_mezo_fa,
            fine=self.un_anno_fa,
            terminazione=Appartenenza.DIMISSIONE,
        )
        x.save()

        self.a.inizio = self.un_anno_fa
        self.a.fine = None
        self.a.precedente = x
        self.a.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato passivo NON contiene volontari con doppia appartenenza valida (DIMISSIONE)"
        )

        x.inizio = self.un_anno_e_mezzo_fa
        x.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato attivo non contiene volontari con doppia appartenenza invalida (DIMISSIONE)"
        )

        self.a.precedente = None
        self.a.save()
        x.delete()

    def test_elettorato_attivo_dimissione_anzianita_soddisfatta(self):

        x = Appartenenza(
            persona=self.p,
            sede=self.s,
            inizio=self.due_anni_e_mezo_fa,
            fine=self.un_anno_fa,
            terminazione=Appartenenza.DIMISSIONE,
        )
        x.save()

        self.a.inizio = self.sei_mesi_fa
        self.a.fine = None
        self.a.precedente = x
        self.a.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo NON contiene volontari con doppia appartenenza valida (DIMISSIONE)"
        )

        x.inizio = self.un_anno_e_mezzo_fa
        x.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo non contiene volontari con doppia appartenenza invalida (DIMISSIONE)"
        )

        self.a.precedente = None
        self.a.save()
        x.delete()

    def test_elettorato_passivo_trasferimento_anzianita_soddisfatta(self):

        x = Appartenenza(
            persona=self.p,
            sede=self.s,
            inizio=self.due_anni_e_mezo_fa,
            fine=self.un_anno_fa,
            terminazione=Appartenenza.TRASFERIMENTO,
        )
        x.save()

        self.a.inizio = self.un_anno_fa
        self.a.fine = None
        self.a.precedente = x
        self.a.save()

        self.assertTrue(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato passivo contiene volontari con doppia appartenenza valida (trasf.)"
        )

        x.inizio = self.un_anno_e_mezzo_fa
        x.save()

        self.assertFalse(
            self._elettorato_contiene(tipo="passivo", persona=self.p),
            "Elettorato attivo non contiene volontari con doppia appartenenza invalida (trasf.)"
        )

        self.a.precedente = None
        self.a.save()
        x.delete()

    def test_dimissione_sostenitore(self):

        presidente = crea_persona()
        crea_utenza(presidente, email=email_fittizzia())
        sostenitore1, sede, a = crea_persona_sede_appartenenza(presidente)
        a.membro = Appartenenza.SOSTENITORE
        a.save()
        socio1 = crea_persona()
        Appartenenza.objects.create(persona=socio1, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)
        sostenitore2 = crea_persona()
        Appartenenza.objects.create(persona=sostenitore2, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)
        socio2 = crea_persona()
        Appartenenza.objects.create(persona=socio2, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        elenco = ElencoSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 in sostenitori)
        self.assertTrue(sostenitore2 in sostenitori)
        self.assertTrue(socio1 not in sostenitori)
        self.assertTrue(socio2 not in sostenitori)

        self.client.login(username=presidente.utenza.email, password='prova')
        data = {
            'info': 'bla bla',
            'motivo': Dimissione.ALTRO
        }
        self.client.post(reverse('us-chiudi-sostenitore', args=(sostenitore1.pk,)), data=data)

        elenco = ElencoSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 not in sostenitori)
        self.assertTrue(sostenitore2 in sostenitori)
        self.assertTrue(socio1 not in sostenitori)
        self.assertTrue(socio2 not in sostenitori)

        elenco = ElencoExSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 in sostenitori)
        self.assertTrue(sostenitore2 not in sostenitori)
        self.assertTrue(socio1 not in sostenitori)
        self.assertTrue(socio2 not in sostenitori)

        Appartenenza.objects.create(persona=sostenitore1, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)

        elenco = ElencoExSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 not in sostenitori)
        self.assertTrue(sostenitore2 not in sostenitori)
        self.assertTrue(socio1 not in sostenitori)
        self.assertTrue(socio2 not in sostenitori)


class TestFunzionaleUfficioSoci(TestFunzionale):

    @skip
    def test_apertura_elenchi(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        # Inizia la sessione
        sessione = self.sessione_utente(persona=delegato)

        elenchi = ['volontari', 'giovani', 'estesi', 'ivcm', 'riserva',
                   'soci', 'sostenitori', 'dipendenti', 'dimessi',
                   'trasferiti', 'elettorato']

        # Vai al pannello soci
        sessione.click_link_by_partial_text("Soci")

        for elenco in elenchi:  # Per ogni elenco

            sessione.visit("%s/us/elenchi/%s/" % (self.live_server_url, elenco))

            # Genera con impostazioni di default (clicca due volte su "Genera")
            sessione.find_by_xpath("//button[@type='submit']").first.click()

            with sessione.get_iframe(0) as iframe:  # Dentro la finestra

                if iframe.is_text_present("Genera elenco"):
                    iframe.find_by_xpath("//button[@type='submit']").first.click()

                self.assertTrue(
                    iframe.is_text_present("Invia messaggio", wait_time=5),
                    msg="Elenco %s apribile da web" % elenco,
                )

    def test_reclama_ordinario(self):

        # Crea oggetti e nomina i delegati US regionali e Locali
        us_regionale = crea_persona()
        us_locale = crea_persona()

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi + datetime.timedelta(days=30)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        ordinario, regionale, appartenenza = crea_persona_sede_appartenenza(presidente=us_regionale)
        appartenenza.membro = Appartenenza.ORDINARIO
        appartenenza.save()
        regionale.estensione = REGIONALE
        regionale.save()

        locale = crea_sede(presidente=us_locale, genitore=regionale)

        sessione_regionale = self.sessione_utente(persona=us_regionale, wait_time=1)
        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=1)

        # Prima di tutto, assicurati che il socio ordinario risulti correttamente
        # nell'elenco del regionale.

        sessione_regionale.click_link_by_partial_text("Soci")
        sessione_regionale.click_link_by_partial_text("Ordinari")

        self.assertTrue(self.presente_in_elenco(sessione_regionale, persona=ordinario),
                        msg="Il socio ordinario è in elenco al regionale")

        # Poi, vai alla procedura di reclamo per il locale e completa.
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Reclama Persona")
        sessione_locale.fill('codice_fiscale', ordinario.codice_fiscale)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        # Completa dati di inizio appartenenza - data nel passato!
        sessione_locale.fill('app-inizio', "1/1/1910")
        sessione_locale.select('app-membro', Appartenenza.SOSTENITORE)
        sessione_locale.select('quota-registra_quota', ModuloReclamaQuota.NO)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        self.assertTrue(sessione_locale.is_text_present("1. Appartenenza al Comitato"),
                        msg="Non e possibile reclamare ordinario nel passato")

        # Compila con la data di oggi.
        sessione_locale.fill('app-inizio', timezone.now().strftime("%d/%m/%Y"))
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        # Controlla elenco dei sostenitori.
        sessione_locale.visit("%s/utente/" % self.live_server_url)
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Sostenitori")
        self.assertTrue(
            self.presente_in_elenco(sessione_locale, persona=ordinario),
            msg="L'ex ordinario è stato reclamato con successo")

        # Controlla la rimozione corretta dagli ordinari.
        sessione_regionale.click_link_by_partial_text("Ordinari")
        self.assertFalse(
            self.presente_in_elenco(sessione_regionale, persona=ordinario),
            msg="L'ex ordinario non è più in elenco al regionale"
        )

    def test_reclama_dipendente(self):

        # Crea oggetti e nomina i delegati US regionali e Locali
        us_locale = crea_persona()

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi + datetime.timedelta(days=30)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        dipendente, sede, appartenenza = crea_persona_sede_appartenenza(presidente=us_locale)
        appartenenza.membro = Appartenenza.DIPENDENTE
        appartenenza.save()

        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=1)

        # Prima di tutto, assicurati che il socio ordinario risulti correttamente
        # nell'elenco del regionale.

        # Poi, vai alla procedura di reclamo per il locale e completa.
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Reclama Persona")
        sessione_locale.fill('codice_fiscale', dipendente.codice_fiscale)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        # Completa dati di inizio appartenenza - data nel passato!
        sessione_locale.fill('app-inizio', "1/1/1910")
        sessione_locale.select('app-membro', Appartenenza.VOLONTARIO)
        sessione_locale.select('quota-registra_quota', ModuloReclamaQuota.NO)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        self.assertTrue(sessione_locale.is_text_present("1. Appartenenza al Comitato"),
                        msg="Non e possibile reclamare dipendente nel passato")

        # Compila con la data di oggi.
        sessione_locale.fill('app-inizio', timezone.now().strftime("%d/%m/%Y"))
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        # Controlla elenco dei volontari.
        sessione_locale.visit("%s/utente/" % self.live_server_url)
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Volontari")
        self.assertTrue(
            self.presente_in_elenco(sessione_locale, persona=dipendente),
            msg="Il dipendente è stato reclamato con successo")
        sessione_locale.click_link_by_partial_text("Dipendenti")
        self.assertTrue(
            self.presente_in_elenco(sessione_locale, persona=dipendente),
            msg="Il dipendente lo è ancora")

    def test_reclama_sostenitore(self):

        # Crea oggetti e nomina i delegati US regionali e Locali
        us_locale = crea_persona()

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi + datetime.timedelta(days=30)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        sostenitore, sede, appartenenza = crea_persona_sede_appartenenza(presidente=us_locale)
        sostenitore.email_contatto = email_fittizzia()
        sostenitore.save()
        appartenenza.membro = Appartenenza.SOSTENITORE
        appartenenza.save()

        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=1)

        # Prima di tutto, assicurati che il socio ordinario risulti correttamente
        # nell'elenco del regionale.

        # Poi, vai alla procedura di reclamo per il locale e completa.
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Reclama Persona")
        sessione_locale.fill('codice_fiscale', sostenitore.codice_fiscale)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        sessione_locale.is_text_present('Questa persona è già registrata come sostenitore')

        sessione_locale.visit('%s/us/dimissioni/sostenitore/%s' % (self.live_server_url, sostenitore.pk))
        sessione_locale.select('motivo', Dimissione.ALTRO)
        sessione_locale.fill('info', "trasforma")
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()
        sessione_locale.is_text_present('Dimissioni registrate')

        self.assertTrue(len(mail.outbox), 1)
        self.assertTrue(sostenitore.email_contatto in mail.outbox[0].to)
        self.assertTrue('Non sei pi&#249; sostenitore di Croce Rossa Italiana' in mail.outbox[0].body)
        self.assertTrue("Altro" in mail.outbox[0].body)
        self.assertTrue("trasforma" in mail.outbox[0].body)
        mail.outbox = []

        sessione_locale.visit('%s/us/reclama/' % (self.live_server_url))
        sessione_locale.fill('codice_fiscale', sostenitore.codice_fiscale)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()
        sessione_locale.is_text_not_present('Questa persona è già registrata come sostenitore')

        # Compila con la data di oggi.
        sessione_locale.fill('app-inizio', timezone.now().strftime("%d/%m/%Y"))
        sessione_locale.select('app-membro', Appartenenza.VOLONTARIO)
        sessione_locale.select('quota-registra_quota', ModuloReclamaQuota.NO)
        sessione_locale.find_by_xpath("//button[@type='submit']").first.click()

        # Controlla elenchi.
        sessione_locale.visit("%s/utente/" % self.live_server_url)
        sessione_locale.click_link_by_partial_text("Soci")
        sessione_locale.click_link_by_partial_text("Volontari")
        self.assertTrue(
            self.presente_in_elenco(sessione_locale, persona=sostenitore),
            msg="Il sostenitore è stato reclamato con successo")
        sessione_locale.click_link_by_partial_text("Sostenitori")
        self.assertFalse(
            self.presente_in_elenco(sessione_locale, persona=sostenitore),
            msg="Il sostenitore non lo è più")
        sessione_locale.click_link_by_partial_text("Ex Sostenitori")
        self.assertTrue(
            self.presente_in_elenco(sessione_locale, persona=sostenitore),
            msg="Il sostenitore è tra gli ex")

    def test_richiedi_tesserino(self, extra_headers={}):
        presidente_locale = crea_persona()
        presidente_provinciale = crea_persona()
        presidente_regionale = crea_persona()
        presidente_nazionale = crea_persona()
        persona = crea_persona()
        locazione = Locazione.objects.create(indirizzo="viale italia 1")
        sede_nazionale = crea_sede(presidente=presidente_nazionale, estensione=NAZIONALE)
        sede_nazionale.locazione = locazione
        sede_nazionale.save()
        sede_regionale = crea_sede(presidente=presidente_regionale, estensione=REGIONALE, genitore=sede_nazionale)
        sede_regionale.locazione = locazione
        sede_regionale.save()
        sede_provinciale = crea_sede(presidente=presidente_provinciale, estensione=PROVINCIALE, genitore=sede_regionale)
        sede_provinciale.locazione = locazione
        sede_provinciale.save()
        sede_locale = crea_sede(presidente=presidente_locale, estensione=PROVINCIALE, genitore=sede_provinciale)
        sede_locale.locazione = locazione
        sede_locale.save()
        appartenenza = crea_appartenenza(persona, sede_locale)
        sessione_persona = self.sessione_utente(persona=persona)
        sessione_persona.visit("%s/utente/fotografia/fototessera/" % self.live_server_url)
        file_obj, filename = tempfile.mkstemp('.jpg')
        file_obj = django.core.files.File(open(filename, 'rb'))

        fototessera = Fototessera.objects.create(
            persona=persona,
            file=file_obj
        )
        self.assertTrue(persona.fototessere.all().exists())
        self.assertEqual(fototessera, persona.fototessera_attuale())
        sessione_persona.reload()
        self.assertTrue(sessione_persona.is_text_present('Storico richieste fototessere'))
        self.assertTrue(sessione_persona.is_text_present('Confermato'))
        self.assertEqual(1, len(sessione_persona.find_by_tag('tbody').find_by_tag('tr')))
        sessione_presidente_locale = self.sessione_utente(persona=presidente_locale)
        sessione_presidente_locale.click_link_by_partial_text("Soci")
        self.assertEqual(1, len(sessione_presidente_locale.find_link_by_href("/us/tesserini/")))
        sessione_presidente_locale.visit("%s/us/tesserini/" % self.live_server_url)
        self.assertEqual(1, len(sessione_presidente_locale.find_link_by_href("/us/tesserini/da-richiedere/")))
        # TODO: richiedere il tesserino cliccando sul link apposito, al momento
        # non è possibile agire sugli elementi della pagina causa probabile timeout
        #sessione_presidente_locale.visit("%s/us/tesserini/da-richiedere/" % self.live_server_url)
        #self.assertTrue(sessione_presidente_locale.is_text_present(persona.nome))
        #self.assertTrue(sessione_presidente_locale.is_text_present(persona.cognome))
        sessione_presidente_locale.visit("%s/us/tesserini/richiedi/%s/" % (self.live_server_url, persona.pk))
        self.assertTrue(sessione_presidente_locale.is_text_present('Richiesta inoltrata'))
        self.assertTrue(sessione_presidente_locale.is_text_present('La richiesta di stampa è stata inoltrata correttamente alla Sede di emissione'))
        self.assertTrue(sessione_presidente_locale.is_text_present(sede_regionale.nome))
        self.assertTrue(sessione_presidente_locale.is_text_present(persona.nome))
        self.assertTrue(sessione_presidente_locale.is_text_present(persona.cognome))
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertTrue(email.subject.find('Richiesta Tesserino inoltrata') > -1)
        self.assertTrue(email.body.find('Il tuo Comitato ha avviato la richiesta di stampa del tuo tesserino.') > -1)
        sessione_presidente_regionale = self.sessione_utente(persona=presidente_regionale)
        sessione_presidente_regionale.visit("%s/us/tesserini/emissione/" % self.live_server_url)
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_richiesta"]//option[@value="ATT"]').first.click()
        sessione_presidente_regionale.find_by_xpath("//button[@type='submit']").first.click()
        sessione_presidente_regionale.find_by_id("seleziona-tutti").first.click()
        sessione_presidente_regionale.find_by_value("lavora").first.click()
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_richiesta"]//option[@value="OK"]').first.click()
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_emissione"]//option[@value="STAMPAT"]').first.click()
        sessione_presidente_regionale.find_by_xpath("//button[@type='submit']").first.click()
        tesserini = Tesserino.objects.all()
        self.assertEqual(1, tesserini.count())
        tesserino = tesserini.first()
        codice_tesserino = tesserino.codice
        self.assertTrue(tesserino.valido)
        self.assertNotEqual(None, codice_tesserino)
        sessione_persona.visit("%s/informazioni/verifica-tesserino/" % self.live_server_url)
        sessione_persona.fill('numero_tessera', codice_tesserino)
        sessione_persona.find_by_xpath("//button[@type='submit']").first.click()
        self.assertTrue(sessione_persona.is_text_present('Tesserino valido'))

        # Richiedi duplicato

        sessione_presidente_locale.visit("%s/us/tesserini/richiedi/%s/" % (self.live_server_url, persona.pk))
        self.assertTrue(sessione_presidente_locale.is_text_present('Richiesta inoltrata'))
        self.assertTrue(sessione_presidente_locale.is_text_present('La richiesta di stampa è stata inoltrata correttamente alla Sede di emissione'))
        self.assertTrue(sessione_presidente_locale.is_text_present(sede_regionale.nome))
        self.assertTrue(sessione_presidente_locale.is_text_present(persona.nome))
        self.assertTrue(sessione_presidente_locale.is_text_present(persona.cognome))
        self.assertEqual(len(mail.outbox), 2)
        email = mail.outbox[1]
        self.assertTrue(email.subject.find('Richiesta Duplicato Tesserino inoltrata') > -1)
        self.assertTrue(email.body.find('Il tuo Comitato ha avviato la richiesta di stampa del duplicato del tuo tesserino.') > -1)
        sessione_presidente_regionale = self.sessione_utente(persona=presidente_regionale)
        sessione_presidente_regionale.visit("%s/us/tesserini/emissione/" % self.live_server_url)
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_richiesta"]//option[@value="ATT"]').first.click()
        sessione_presidente_regionale.find_by_xpath("//button[@type='submit']").first.click()
        sessione_presidente_regionale.find_by_id("seleziona-tutti").first.click()
        sessione_presidente_regionale.find_by_value("lavora").first.click()
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_richiesta"]//option[@value="OK"]').first.click()
        sessione_presidente_regionale.find_by_xpath('//select[@name="stato_emissione"]//option[@value="STAMPAT"]').first.click()
        sessione_presidente_regionale.find_by_xpath("//button[@type='submit']").first.click()
        tesserino_duplicato = Tesserino.objects.exclude(codice=codice_tesserino).first()
        tesserino_vecchio = Tesserino.objects.filter(codice=codice_tesserino).first()
        self.assertEqual(Tesserino.DUPLICATO, tesserino_duplicato.tipo_richiesta)
        self.assertNotEqual(Tesserino.DUPLICATO, tesserino.tipo_richiesta)
        self.assertTrue(tesserino_duplicato.valido)
        self.assertFalse(tesserino_vecchio.valido)
        sessione_persona.visit("%s/informazioni/verifica-tesserino/" % self.live_server_url)
        sessione_persona.fill('numero_tessera', codice_tesserino)
        sessione_persona.find_by_xpath("//button[@type='submit']").first.click()
        self.assertTrue(sessione_persona.is_text_present('Tesserino non valido'))
        sessione_persona.fill('numero_tessera', tesserino_duplicato.codice)
        sessione_persona.find_by_xpath("//button[@type='submit']").first.click()
        self.assertTrue(sessione_persona.is_text_present('Tesserino valido'))

    @freeze_time('2016-11-14')
    def test_registrazione_quota_socio_senza_fine(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8,
            quota_benemerito=8, quota_aspirante=8, quota_sostenitore=8
        )

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': (oggi - datetime.timedelta(days=60)).strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))
        quota = Quota.objects.get(persona=volontario)
        self.assertFalse(quota.riduzione)
        self.assertEqual(quota.tipo, Quota.QUOTA_SOCIO)
        self.assertEqual(quota.importo_extra, 0)
        self.assertEqual(quota.causale_extra, '')

    @freeze_time('2016-11-14')
    def test_registrazione_quota_soci(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario1, sede, appartenenza = crea_persona_sede_appartenenza()
        volontario2 = crea_persona()
        crea_appartenenza(volontario2, sede)

        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)

        tesseramento = Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8,
            quota_benemerito=8, quota_aspirante=8, quota_sostenitore=8
        )
        riduzione = Riduzione.objects.create(
            nome='Riduzione di test', quota=2, descrizione='Descrizione riduzione', tesseramento=tesseramento
        )

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        self.client.login(email="mario@rossi.it", password="prova")

        data = {
            'volontario': volontario1.pk,
            'riduzione': riduzione.pk,
            'importo': 3,
            'data_versamento': (oggi - datetime.timedelta(days=60)).strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))
        quota = Quota.objects.get(persona=volontario1)
        self.assertEqual(quota.tipo, Quota.QUOTA_SOCIO)
        self.assertEqual(quota.importo_extra, 1)
        self.assertEqual(quota.riduzione, riduzione)
        self.assertEqual(quota.causale_extra, 'Donazione')
        self.assertTrue(riduzione.descrizione in  quota.causale)

        data = {
            'volontario': volontario2.pk,
            'riduzione': '',
            'importo': 13,
            'data_versamento': (oggi - datetime.timedelta(days=60)).strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))
        quota = Quota.objects.get(persona=volontario2)
        self.assertEqual(quota.tipo, Quota.QUOTA_SOCIO)
        self.assertEqual(quota.importo_extra, 5)
        self.assertFalse(quota.riduzione)
        self.assertTrue(riduzione.descrizione not in quota.causale)

    @freeze_time('2016-11-14')
    def test_registrazione_quota_socio_senza_fine_chiuso(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)

        Tesseramento.objects.create(
            stato=Tesseramento.CHIUSO, inizio=inizio_anno,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8,
            quota_benemerito=8, quota_aspirante=8, quota_sostenitore=8
        )

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': (oggi - datetime.timedelta(days=60)).strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # tesseramento chiuso, quota non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tesseramento {} è chiuso'.format(oggi.year))

    @freeze_time('2016-11-14')
    def test_registrazione_quota_socio(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'successiva al {}'.format(fine_soci.strftime('%Y-%m-%d')))

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': fine_soci.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Necessario impostare indirizzo del Comitato')

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': fine_soci.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

    @freeze_time('2017-01-14')
    def test_registrazione_quota_socio_inizio_anno(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        post_fine_soci = fine_soci + datetime.timedelta(days=2)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': post_fine_soci.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'non può essere nel futuro')

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Necessario impostare indirizzo del Comitato')

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

    @freeze_time('2016-11-14')
    def test_registrazione_quota_socio_iv(self):
        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, __ = crea_persona_sede_appartenenza()
        volontario_iv_1 = crea_persona()
        crea_appartenenza(volontario_iv_1, sede)
        volontario_iv_1.iv = True
        volontario_iv_1.save()
        volontario_iv_2 = crea_persona()
        crea_appartenenza(volontario_iv_2, sede)
        volontario_iv_2.iv = True
        volontario_iv_2.save()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi - datetime.timedelta(days=60)
        fine_soci_iv = oggi - datetime.timedelta(days=30)
        data_1 = fine_soci_iv - datetime.timedelta(days=10)
        data_2 = fine_soci - datetime.timedelta(days=10)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            fine_soci_iv=fine_soci_iv, anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8,
            quota_benemerito=8, quota_aspirante=8, quota_sostenitore=8
        )

        # registrazione con data odierna bloccata per entrambi
        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'successiva al {}'.format(fine_soci.strftime('%Y-%m-%d')))

        data = {
            'volontario': volontario_iv_1.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'successiva al {}'.format(fine_soci_iv.strftime('%Y-%m-%d')))

        # registrazione con data di un mese fa bloccata solo per soci normali
        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': data_1.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'successiva al {}'.format(fine_soci.strftime('%Y-%m-%d')))

        data = {
            'volontario': volontario_iv_1.pk,
            'importo': 8,
            'data_versamento': data_1.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

        # registrazione con data di due mesi fa bloccata solo per soci normali
        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': data_2.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

        data = {
            'volontario': volontario_iv_2.pk,
            'importo': 8,
            'data_versamento': data_2.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

        data = {
            'volontario': volontario_iv_1.pk,
            'importo': 8,
            'data_versamento': data_1.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')),
                                    data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Questo volontario ha già pagato la Quota associativa '
                                      'per l&#39;anno {}'.format(oggi.year))

    @freeze_time('2016-11-14')
    def pagamento_quota_nuovo_volontario(self):
        """
        Testa che un nuovo volontario sia in grado di registarare
        la quota nell'anno in cui è diventato volontario
        """
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()

        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)
        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        appartenenza.inizio = poco_fa().replace(month=8)
        appartenenza.save()

        oggi = poco_fa().replace(month=9)
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        fine_anno = inizio_anno.replace(month=12) - datetime.timedelta(days=31)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8, fine_soci_nv=fine_anno
        )

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

    @freeze_time('2016-11-14')
    def pagamento_quota_vecchio_volontario(self):
        """
        Testa che un vecchio volontario non sia in grado di registarare
        la quota oltre la scadenza
        """
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()

        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)
        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        appartenenza.inizio = poco_fa().replace(year=2)
        appartenenza.save()

        oggi = poco_fa().replace(month=9)
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        fine_anno = inizio_anno.replace(month=12) - datetime.timedelta(days=31)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8, fine_soci_nv=fine_anno
        )

        data = {
            'volontario': volontario.pk,
            'importo': 8,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'successiva al {}'.format(fine_soci.strftime('%Y-%m-%d')))
