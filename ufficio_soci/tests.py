import datetime
from unittest import skip

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_text

from anagrafica.costanti import REGIONALE
from anagrafica.models import Appartenenza, Sede, Persona
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from autenticazione.utils_test import TestFunzionale
from base.geo import Locazione
from base.utils import poco_fa
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, \
    crea_utenza, crea_locazione
from ufficio_soci.elenchi import ElencoElettoratoAlGiorno
from ufficio_soci.forms import ModuloElencoElettorato, ModuloReclamaQuota
from ufficio_soci.models import Tesseramento


class TestBase(TestCase):

    def setUp(self):
        self.p, self.s, self.a = crea_persona_sede_appartenenza()

        self.oggi = datetime.date(2015, 1, 1)
        self.quindici_anni_fa = (datetime.date(2000, 1, 1))
        self.venti_anni_fa = (datetime.date(1995, 1, 1))
        self.due_anni_e_mezo_fa = datetime.date(2012, 6, 15)
        self.un_anno_fa = datetime.date(2014, 1, 1)
        self.un_anno_e_mezzo_fa = datetime.date(2013, 6, 15)

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

        self.a.inizio = self.un_anno_fa
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
            fine=self.un_anno_fa,
            terminazione=Appartenenza.TRASFERIMENTO,
        )
        x.save()

        self.a.inizio = self.un_anno_fa
        self.a.fine = None
        self.a.precedente = x
        self.a.save()

        self.assertTrue(
            self._elettorato_contiene(tipo="attivo", persona=self.p),
            "Elettorato attivo contiene volontari con doppia appartenenza valida (trasf.)"
        )

        x.inizio = self.un_anno_e_mezzo_fa
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

        self.a.inizio = self.un_anno_fa
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


class TestFunzionaleUfficioSoci(TestFunzionale):

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
        fine_soci = oggi.replace(month=oggi.month + 1)

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

        sessione_regionale = self.sessione_utente(persona=us_regionale)
        sessione_locale = self.sessione_utente(persona=us_locale)

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

    def test_registrazione_quota_socio_senza_fine(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi.replace(month=oggi.month - 1)

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
            'data_versamento': oggi.replace(month=oggi.month-2).strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

    def test_registrazione_quota_socio_senza_fine_chiuso(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi.replace(month=oggi.month - 1)

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
            'data_versamento': oggi.replace(month=oggi.month-2).strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # tesseramento chiuso, quota non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tesseramento {} è chiuso'.format(oggi.year))

    def test_registrazione_quota_socio(self):

        # Crea oggetti e nomina il delegato US
        delegato = crea_persona()
        utente = crea_utenza(delegato, email="mario@rossi.it", password="prova")
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = oggi.replace(month=oggi.month - 1)

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
            'data_versamento': oggi.replace(month=oggi.month-2).strftime('%d/%m/%Y')
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
            'data_versamento': oggi.replace(month=oggi.month-2).strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_quote_nuova')), data=data)
        # quota registrata con successo
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

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
        fine_soci = oggi.replace(month=oggi.month - 2)
        fine_soci_iv = oggi.replace(month=oggi.month - 1)
        data_1 = oggi.replace(month=oggi.month - 1, day=1)
        data_2 = oggi.replace(month=oggi.month - 2, day=1)

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
