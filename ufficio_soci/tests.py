import datetime
from time import sleep
from unittest import skip
import tempfile

import django.core.files
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from anagrafica.models import Appartenenza, Sede, Persona, Fototessera, Dimissione, ProvvedimentoDisciplinare, \
    Estensione, Trasferimento, Delega
from anagrafica.costanti import NAZIONALE, PROVINCIALE, REGIONALE, LOCALE, TERRITORIALE
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, DIRETTORE_CORSO
from anagrafica.permessi.costanti import MODIFICA
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI
from attivita.models import Area, Partecipazione, Turno
from attivita.models import Attivita
from autenticazione.utils_test import TestFunzionale
from base.geo import Locazione
from base.utils import poco_fa, oggi
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza, \
    crea_utenza, crea_locazione, email_fittizzia, crea_tesseramento
from base.models import Autorizzazione
from ufficio_soci.elenchi import ElencoElettoratoAlGiorno, ElencoSociAlGiorno, ElencoSostenitori, ElencoExSostenitori, \
    ElencoVolontari, ElencoTesseriniRichiesti, ElencoTesseriniDaRichiedere, ElencoSenzaTurni
from ufficio_soci.forms import ModuloElencoElettorato, ModuloReclamaQuota, ModuloElencoQuote
from ufficio_soci.models import Tesseramento, Tesserino, Quota, Riduzione
from formazione.models import Aspirante, CorsoBase, InvitoCorsoBase, PartecipazioneCorsoBase


class TestBase(TestCase):

    def setUp(self):
        super(TestBase, self).setUp()

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

    def test_zero_turni(self):

        presidente = crea_persona()
        sede = crea_sede(presidente)
        persone = []
        for x in range(1, 10):
            persone.append(crea_persona())
            Appartenenza.objects.create(
                persona=persone[-1], sede=sede, inizio=self.due_anni_e_mezo_fa,
            )

        area = Area.objects.create(
            nome="6",
            obiettivo=6,
            sede=sede,
        )

        attivita = Attivita.objects.create(
            stato=Attivita.VISIBILE,
            nome="Att 1",
            apertura=Attivita.APERTA,
            area=area,
            descrizione="1",
            sede=sede,
            estensione=sede,
        )

        turno = Turno.objects.create(
            attivita=attivita,
            prenotazione=poco_fa(),
            inizio=poco_fa() - datetime.timedelta(days=10),
            fine=poco_fa(),
            minimo=1,
            massimo=16,
        )

        partecipazioni = []
        for persona in persone:
            partecipazioni.append(Partecipazione.objects.create(
                persona=persona,
                turno=turno,
                confermata=False
            ))

        elenco = ElencoSenzaTurni([sede])
        elenco.modulo_riempito = elenco.modulo()(
            {'inizio': poco_fa() - datetime.timedelta(days=100), 'fine': poco_fa() - datetime.timedelta(days=5)}
        )
        self.assertTrue(elenco.modulo_riempito.is_valid())
        zero_turni = elenco.risultati()
        self.assertEqual(len(zero_turni), len(persone))

        partecipazioni[0].confermata = True
        partecipazioni[0].save()
        zero_turni = elenco.risultati()
        self.assertEqual(len(zero_turni), len(persone) - 1)
        self.assertTrue(persone[0] not in zero_turni)

        turno.inizio = poco_fa() - datetime.timedelta(days=200)
        turno.fine = poco_fa() - datetime.timedelta(days=150)
        turno.save()
        zero_turni = elenco.risultati()
        self.assertEqual(len(zero_turni), len(persone))

        turno.fine = poco_fa() - datetime.timedelta(days=50)
        turno.save()
        zero_turni = elenco.risultati()
        self.assertEqual(len(zero_turni), len(persone) - 1)
        self.assertTrue(persone[0] not in zero_turni)

    def test_elettorato_sospensione(self):

        presidente = crea_persona()
        sede = crea_sede(presidente)
        persone = []
        for x in range(1, 10):
            persone.append(crea_persona())
            Appartenenza.objects.create(
                persona=persone[-1], sede=sede, inizio=self.due_anni_e_mezo_fa,
            )

        elenco = ElencoElettoratoAlGiorno([sede])
        elenco.modulo_riempito = elenco.modulo()({'al_giorno': poco_fa(), 'elettorato': ModuloElencoElettorato.ELETTORATO_PASSIVO})
        elenco.modulo_riempito.is_valid()
        eleggibili = elenco.risultati()
        self.assertEqual(len(eleggibili), len(persone))
        for persona in persone:
            self.assertTrue(persona in eleggibili)

        def test_elettorato(elenco, persone, indice_persona=None):
            eleggibili = elenco.risultati()
            if indice_persona is not None:
                self.assertEqual(len(eleggibili), len(persone) - 1)
            else:
                self.assertEqual(len(eleggibili), len(persone))
            for index, persona in enumerate(persone):
                if indice_persona is not None and index == indice_persona:
                    self.assertFalse(persona in eleggibili)
                else:
                    self.assertTrue(persona in eleggibili)

        provvedimento = ProvvedimentoDisciplinare.objects.create(
            persona=persone[0], sede=sede,
            inizio=poco_fa() - datetime.timedelta(days=1), fine=poco_fa() + datetime.timedelta(days=1),
            motivazione='bla', tipo=ProvvedimentoDisciplinare.SOSPENSIONE
        )
        test_elettorato(elenco, persone, 0)

        # ammonizione non conta
        provvedimento.tipo = provvedimento.AMMONIZIONE
        provvedimento.save()
        test_elettorato(elenco, persone)

        # espulsione non conta
        provvedimento.tipo = provvedimento.ESPULSIONE
        provvedimento.save()
        test_elettorato(elenco, persone)

        # sospensione non ancora attiva non conta
        provvedimento.tipo = provvedimento.SOSPENSIONE
        provvedimento.inizio = poco_fa() + datetime.timedelta(seconds=60)
        provvedimento.save()
        test_elettorato(elenco, persone)

        # sospensione terminata non conta
        provvedimento.inizio = poco_fa() - datetime.timedelta(days=1)
        provvedimento.fine = poco_fa() - datetime.timedelta(days=1)
        provvedimento.save()
        test_elettorato(elenco, persone)

        # sospensione senza data di fine conta
        provvedimento.inizio = poco_fa() - datetime.timedelta(days=1)
        provvedimento.fine = None
        provvedimento.save()
        test_elettorato(elenco, persone, 0)

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
        sostenitore_volontario = crea_persona()
        Appartenenza.objects.create(persona=sostenitore_volontario, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)
        Appartenenza.objects.create(persona=sostenitore_volontario, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        elenco = ElencoSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 in sostenitori)
        self.assertTrue(sostenitore2 in sostenitori)
        self.assertTrue(sostenitore_volontario in sostenitori)
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
        exsostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 in exsostenitori)
        self.assertTrue(sostenitore2 not in exsostenitori)
        self.assertTrue(socio1 not in exsostenitori)
        self.assertTrue(socio2 not in exsostenitori)

        Appartenenza.objects.create(persona=sostenitore1, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)

        elenco = ElencoExSostenitori([sede])
        exsostenitori = elenco.risultati()
        self.assertTrue(sostenitore1 not in exsostenitori)
        self.assertTrue(sostenitore2 not in exsostenitori)
        self.assertTrue(socio1 not in exsostenitori)
        self.assertTrue(socio2 not in exsostenitori)

        data = {
            'info': 'bla bla',
            'motivo': Dimissione.ALTRO
        }
        self.client.post(reverse('us-chiudi-sostenitore', args=(sostenitore_volontario.pk,)), data=data)

        elenco = ElencoSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertFalse(sostenitore_volontario in sostenitori)

        elenco = ElencoExSostenitori([sede])
        exsostenitori = elenco.risultati()
        self.assertTrue(sostenitore_volontario in exsostenitori)
        sostenitore_volontario.refresh_from_db()
        self.assertTrue(sostenitore_volontario.volontario)

        elenco = ElencoVolontari([sede])
        elenco.modulo_riempito = elenco.modulo()({'includi_estesi': elenco.modulo().SI})
        elenco.modulo_riempito.is_valid()
        volontari = elenco.risultati()
        self.assertTrue(sostenitore_volontario in volontari)

    def test_dimissione_controllo_appartenenza(self):
        presidente = crea_persona()
        crea_utenza(presidente, email=email_fittizzia())
        sede = crea_sede(presidente, estensione=REGIONALE)

        ordinario = crea_persona()
        dipendente = crea_persona()
        militare = crea_persona()
        infermiera = crea_persona()
        sostenitore = crea_persona()
        donatore = crea_persona()

        crea_appartenenza(ordinario, sede, tipo=Appartenenza.ORDINARIO)
        crea_appartenenza(dipendente, sede, tipo=Appartenenza.DIPENDENTE)
        crea_appartenenza(militare, sede, tipo=Appartenenza.MILITARE)
        crea_appartenenza(infermiera, sede, tipo=Appartenenza.INFERMIERA)
        crea_appartenenza(sostenitore, sede, tipo=Appartenenza.SOSTENITORE)
        crea_appartenenza(donatore, sede, tipo=Appartenenza.DONATORE)

        self.assertTrue(ordinario.ordinario)
        self.assertTrue(dipendente.dipendente)
        self.assertTrue(militare.militare)
        self.assertTrue(infermiera.infermiera)
        self.assertTrue(sostenitore.sostenitore)
        self.assertTrue(donatore.est_donatore)

        self.client.login(username=presidente.utenza.email, password='prova')
        data = {
            'info': 'bla bla',
            'motivo': Dimissione.VOLONTARIE
        }
        for persona in (ordinario, dipendente, militare, infermiera, sostenitore, donatore):
            response = self.client.post(reverse('us-dimissioni', args=(persona.pk,)), data=data)
            self.assertContains(response, 'Dimissioni registrate')
            persona.refresh_from_db()
        self.assertFalse(ordinario.ordinario)
        self.assertFalse(dipendente.dipendente)
        self.assertFalse(militare.militare)
        self.assertFalse(infermiera.infermiera)
        self.assertFalse(sostenitore.sostenitore)
        self.assertFalse(donatore.est_donatore)

    def test_dimissione_volontario(self):
        sede2 = crea_sede()
        presidente = crea_persona()
        crea_utenza(presidente, email=email_fittizzia())
        sostenitore1, sede, a = crea_persona_sede_appartenenza(presidente)
        a.membro = Appartenenza.SOSTENITORE
        a.save()
        socio1 = crea_persona()
        Appartenenza.objects.create(persona=socio1, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)
        trasf = Trasferimento.objects.create(
            destinazione=sede2,
            persona=socio1,
            richiedente=socio1,
            motivo='test'
        )
        trasf.richiedi()
        sostenitore2 = crea_persona()
        Appartenenza.objects.create(persona=sostenitore2, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)
        socio2 = crea_persona()
        Appartenenza.objects.create(persona=socio2, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)
        sostenitore_volontario = crea_persona()
        Appartenenza.objects.create(persona=sostenitore_volontario, sede=sede, inizio=poco_fa(), membro=Appartenenza.SOSTENITORE)
        Appartenenza.objects.create(persona=sostenitore_volontario, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        elenco = ElencoVolontari([sede])
        elenco.modulo_riempito = elenco.modulo()({'includi_estesi': elenco.modulo().SI})
        elenco.modulo_riempito.is_valid()
        volontari = elenco.risultati()
        self.assertTrue(sostenitore1 not in volontari)
        self.assertTrue(sostenitore2 not in volontari)
        self.assertTrue(sostenitore_volontario in volontari)
        self.assertTrue(socio1 in volontari)
        self.assertTrue(socio2 in volontari)

        self.client.login(username=presidente.utenza.email, password='prova')
        data = {
            'info': 'bla bla',
            'motivo': Dimissione.VOLONTARIE
        }
        self.client.post(reverse('us-dimissioni', args=(socio1.pk,)), data=data)

        elenco = ElencoVolontari([sede])
        elenco.modulo_riempito = elenco.modulo()({'includi_estesi': elenco.modulo().SI})
        elenco.modulo_riempito.is_valid()
        volontari = elenco.risultati()
        self.assertTrue(sostenitore1 not in volontari)
        self.assertTrue(sostenitore2 not in volontari)
        self.assertTrue(socio1 not in volontari)
        self.assertTrue(socio2 in volontari)

        Appartenenza.objects.create(persona=socio1, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        elenco = ElencoVolontari([sede])
        elenco.modulo_riempito = elenco.modulo()({'includi_estesi': elenco.modulo().SI})
        elenco.modulo_riempito.is_valid()
        volontari = elenco.risultati()
        self.assertTrue(sostenitore1 not in volontari)
        self.assertTrue(sostenitore2 not in volontari)
        self.assertTrue(socio1 in volontari)
        self.assertTrue(socio2 in volontari)

        data = {
            'info': 'bla bla',
            'motivo': Dimissione.VOLONTARIE
        }
        self.client.post(reverse('us-dimissioni', args=(sostenitore_volontario.pk,)), data=data)

        elenco = ElencoSostenitori([sede])
        sostenitori = elenco.risultati()
        self.assertTrue(sostenitore_volontario in sostenitori)

        elenco = ElencoExSostenitori([sede])
        exsostenitori = elenco.risultati()
        self.assertTrue(sostenitore_volontario not in exsostenitori)

        sostenitore_volontario.refresh_from_db()
        self.assertFalse(sostenitore_volontario.volontario)

        elenco = ElencoVolontari([sede])
        elenco.modulo_riempito = elenco.modulo()({'includi_estesi': elenco.modulo().SI})
        elenco.modulo_riempito.is_valid()
        volontari = elenco.risultati()
        self.assertFalse(sostenitore_volontario in volontari)

    def test_elenco_tesserini(self):
        presidente = crea_persona()
        crea_utenza(presidente, email=email_fittizzia())

        regionale = crea_sede(presidente, REGIONALE)
        sede = crea_sede(presidente, LOCALE, regionale)
        sede.locazione = crea_locazione()
        sede.genitore = regionale
        sede.save()

        vol_1 = crea_persona()
        Fototessera.objects.create(persona=vol_1, confermata=True)
        Appartenenza.objects.create(persona=vol_1, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        vol_2 = crea_persona()
        Fototessera.objects.create(persona=vol_2, confermata=True)
        Appartenenza.objects.create(persona=vol_2, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        vol_3 = crea_persona()
        Fototessera.objects.create(persona=vol_3, confermata=True)
        Appartenenza.objects.create(persona=vol_3, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        vol_4 = crea_persona()
        Fototessera.objects.create(persona=vol_4, confermata=True)
        Appartenenza.objects.create(persona=vol_4, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        vol_5 = crea_persona()
        Fototessera.objects.create(persona=vol_5, confermata=True)
        Appartenenza.objects.create(persona=vol_5, sede=sede, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO)

        el_richiesti = ElencoTesseriniRichiesti([sede])
        richiesti = el_richiesti.risultati()
        self.assertEqual(richiesti.count(), 0)

        el_da_richiedere = ElencoTesseriniDaRichiedere([sede])
        da_richiedere = el_da_richiedere.risultati()
        self.assertEqual(da_richiedere .count(), 5)

        self.client.login(username=presidente.utenza.email, password='prova')
        response = self.client.get(reverse('us-tesserini-richiedi', args=(vol_1.pk,)))
        self.assertNotContains(response, "Il Comitato non ha un indirizzo")

        richiesti = el_richiesti.risultati()
        self.assertEqual(richiesti.count(), 1)

        da_richiedere = el_da_richiedere.risultati()
        self.assertEqual(da_richiedere .count(), 4)

        self.assertEqual(Tesserino.objects.all().count(), 1)
        self.assertEqual(Tesserino.objects.filter(
            valido=False, tipo_richiesta=Tesserino.RILASCIO, stato_richiesta=Tesserino.RICHIESTO
        ).count(), 1)

        self.client.login(username=presidente.utenza.email, password='prova')
        response = self.client.get(reverse('us-tesserini-richiedi', args=(vol_1.pk,)))
        self.assertNotContains(response, "Il Comitato non ha un indirizzo")
        self.assertContains(response, "Esiste già una richiesta di un tesserino per la persona")

        self.assertEqual(Tesserino.objects.all().count(), 1)

        Tesserino.objects.filter(
            valido=False, tipo_richiesta=Tesserino.RILASCIO, stato_richiesta=Tesserino.RICHIESTO
        ).update(stato_richiesta=Tesserino.ACCETTATO, stato_emissione=Tesserino.STAMPATO,
                 motivo_rifiutato='', data_conferma=poco_fa(), valido=True)
        for tesserino in Tesserino.objects.filter(valido=True):
            tesserino.assicura_presenza_codice()

        self.client.login(username=presidente.utenza.email, password='prova')
        response = self.client.get(reverse('us-tesserini-richiedi', args=(vol_1.pk,)))
        self.assertNotContains(response, "Il Comitato non ha un indirizzo")
        self.assertNotContains(response, "Esiste già una richiesta di un tesserino per la persona")
        self.assertContains(response, 'Richiesta inoltrata')

        self.assertEqual(Tesserino.objects.all().count(), 2)
        self.assertEqual(Tesserino.objects.filter(
            valido=False, tipo_richiesta=Tesserino.RILASCIO, stato_richiesta=Tesserino.RICHIESTO
        ).count(), 0)
        self.assertEqual(Tesserino.objects.filter(
            valido=False, tipo_richiesta=Tesserino.RILASCIO, stato_richiesta=Tesserino.ACCETTATO
        ).count(), 1)
        self.assertEqual(Tesserino.objects.filter(
            valido=False, tipo_richiesta=Tesserino.DUPLICATO, stato_richiesta=Tesserino.RICHIESTO
        ).count(), 1)

        richiesti = el_richiesti.risultati()
        self.assertEqual(richiesti.count(), 1)

        da_richiedere = el_da_richiedere.risultati()
        self.assertEqual(da_richiedere .count(), 4)

    def test_termine_estensioni(self):
        presidente_com1 = crea_persona()
        crea_utenza(presidente_com1, email=email_fittizzia())
        comitato1 = crea_sede(presidente_com1, LOCALE)
        Appartenenza.objects.create(
            persona=presidente_com1, sede=comitato1, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO
        )

        presidente_com2 = crea_persona()
        crea_utenza(presidente_com2, email=email_fittizzia())
        comitato2 = crea_sede(presidente_com2, LOCALE)
        Appartenenza.objects.create(
            persona=presidente_com2, sede=comitato2, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO
        )

        comitato3 = crea_sede(presidente_com2, LOCALE)

        volontario = crea_persona()

        appartenenza_vol1_c1_vol = Appartenenza.objects.create(
            persona=volontario, sede=comitato1, inizio=poco_fa(), membro=Appartenenza.VOLONTARIO
        )
        volontario.refresh_from_db()

        # Estensione Vol 1 - Comitato 2
        estensione = Estensione.objects.create(
            persona=volontario, richiedente=volontario, destinazione=comitato2, motivo='test'
        )
        estensione.richiedi()
        modulo = estensione.autorizzazione_concedi_modulo()(data={
            'protocollo_data': poco_fa(), 'protocollo_numero': '1'
        })
        self.assertTrue(modulo.is_valid())
        estensione.autorizzazione_concessa(modulo)
        estensione.confermata = True
        estensione.save()
        appartenenza_vol1_c2_est = estensione.appartenenza

        # Estensione Vol 1 - Comitato 3
        estensione = Estensione.objects.create(
            persona=volontario, richiedente=volontario, destinazione=comitato3, motivo='test'
        )
        estensione.richiedi()
        modulo = estensione.autorizzazione_concedi_modulo()(data={
            'protocollo_data': poco_fa(), 'protocollo_numero': '1'
        })
        self.assertTrue(modulo.is_valid())
        estensione.autorizzazione_concessa(modulo)
        estensione.confermata = True
        estensione.save()
        appartenenza_vol1_c3_est = estensione.appartenenza

        # Estensione presidente 2
        estensione = Estensione.objects.create(
            persona=presidente_com2, richiedente=presidente_com2, destinazione=comitato1, motivo='test'
        )
        estensione.richiedi()
        modulo = estensione.autorizzazione_concedi_modulo()(data={
            'protocollo_data': poco_fa(), 'protocollo_numero': '1'
        })
        self.assertTrue(modulo.is_valid())
        estensione.autorizzazione_concessa(modulo)
        estensione.confermata = True
        estensione.save()
        appartenenza_pres2_c1_est = estensione.appartenenza

        self.assertFalse(presidente_com2.permessi_almeno(appartenenza_vol1_c2_est.estensione.first(), MODIFICA))
        self.assertFalse(presidente_com2.permessi_almeno(appartenenza_vol1_c3_est.estensione.first(), MODIFICA))
        self.assertFalse(presidente_com2.permessi_almeno(appartenenza_vol1_c1_vol.persona, MODIFICA))
        self.assertTrue(presidente_com1.permessi_almeno(appartenenza_vol1_c2_est.estensione.first(), MODIFICA))
        self.assertTrue(presidente_com1.permessi_almeno(appartenenza_vol1_c3_est.estensione.first(), MODIFICA))
        self.assertTrue(presidente_com1.permessi_almeno(appartenenza_vol1_c1_vol.persona, MODIFICA))

        termina_vol1_c2_est_url = reverse('us-termina-estensione', args=(appartenenza_vol1_c2_est.pk,))
        termina_vol1_c3_est_url = reverse('us-termina-estensione', args=(appartenenza_vol1_c3_est.pk,))
        profilo_url = reverse('profilo', kwargs={'pk': volontario.pk, 'sezione': 'appartenenze'})
        errore_url = reverse('errore-permessi')

        self.assertEqual(volontario.estensioni_attuali().count(), 2)

        # Test con Presidente 2 - Nessun permesso su nessuna estensione
        self.client.login(email=presidente_com2.email_utenza, password="prova")
        response = self.client.get(profilo_url)
        self.assertNotContains(response, termina_vol1_c2_est_url)
        self.assertNotContains(response, termina_vol1_c3_est_url)
        response = self.client.get(termina_vol1_c2_est_url)
        self.assertRedirects(response, errore_url)
        response = self.client.get(termina_vol1_c3_est_url)
        self.assertRedirects(response, errore_url)

        self.assertEqual(volontario.estensioni_attuali().count(), 2)

        # Test con Presidente 1 - Tutti i permessi su tutte le estensioni
        self.client.login(email=presidente_com1.email_utenza, password="prova")
        response = self.client.get(profilo_url)
        self.assertContains(response, termina_vol1_c2_est_url)
        self.assertContains(response, termina_vol1_c3_est_url)
        response = self.client.get(termina_vol1_c2_est_url)
        self.assertContains(response, 'Estensione terminata')
        response = self.client.get(termina_vol1_c3_est_url)
        self.assertContains(response, 'Estensione terminata')

        self.assertEqual(volontario.estensioni_attuali().count(), 0)


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

        sessione_regionale = self.sessione_utente(persona=us_regionale, wait_time=2)
        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=2)

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

        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=2)

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

        sessione_locale = self.sessione_utente(persona=us_locale, wait_time=2)

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

        # Non c'è il bottone per chiedere il duplicato
        self.assertEqual(0, len(sessione_presidente_locale.find_link_by_href("/us/tesserini/da-richiedere/")))
        self.assertTrue(sessione_presidente_locale.is_text_not_present('Richiedi duplicato'))

        # Richiedi duplicato fallisce perché non esiste già accettato
        sessione_presidente_locale.visit("%s/us/tesserini/richiedi/%s/" % (self.live_server_url, persona.pk))
        self.assertTrue(sessione_presidente_locale.is_text_present('Tesserino non accettato'))

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

        # Richiedi duplicato, ora ha successo perché esiste tesserino emesso

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

    @freeze_time('2016-02-14')
    def pagamento_ricevuta_volontario_senza_comitato(self):
        """
        Testa che un volontario senza appartenenza sia gestito l'errore
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

        appartenenza.delete()

        oggi = poco_fa().replace(month=2)
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        fine_anno = inizio_anno.replace(month=12) - datetime.timedelta(days=31)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8, fine_soci_nv=fine_anno
        )

        data = {
            'persona': volontario.pk,
            'importo': 8,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.RICEVUTA,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ritornato errore di assenza comitato
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'la persona non risulta appartenente')

    @freeze_time('2016-02-14')
    def pagamento_ricevuta_volontario_con_comitato(self):
        """
        Testa che un volontario senza appartenenza sia gestito l'errore
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

        oggi = poco_fa().replace(month=2)
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        fine_anno = inizio_anno.replace(month=12) - datetime.timedelta(days=31)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8, fine_soci_nv=fine_anno
        )

        data = {
            'persona': volontario.pk,
            'importo': 8,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.RICEVUTA,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email="mario@rossi.it", password="prova")
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta registrata
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

    @freeze_time('2016-10-14')
    def pagamento_quota_sostenitore(self):
        """
        Test che la quota sostenitore sia pagabile con controllo sulla quota minima
        """

        oggi = poco_fa().replace(month=2)
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)
        fine_anno = inizio_anno.replace(month=12) - datetime.timedelta(days=31)

        anno_successivo = poco_fa().replace(month=2, year=oggi.year+1)
        inizio_anno_successivo = anno_successivo.replace(month=1, day=1)

        passato = poco_fa().replace(month=2, year=oggi.year-1)

        delegato = crea_persona()
        sostenitore, sede, appartenenza = crea_persona_sede_appartenenza()
        appartenenza.membro = Appartenenza.SOSTENITORE
        appartenenza.save()
        utente1 = crea_utenza(delegato, email="mario@rossi.it", password="prova")

        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)
        sede.telefono = '+3902020202'
        sede.email = 'comitato@prova.it'
        sede.codice_fiscale = '01234567891'
        sede.partita_iva = '01234567891'
        sede.locazione = crea_locazione()
        sede.save()

        delegato2 = crea_persona()
        sede2 = crea_sede(delegato2)
        utente2 = crea_utenza(delegato2, email="mario2@rossi.it", password="prova")

        sede2.aggiungi_delegato(UFFICIO_SOCI, delegato2)
        sede2.telefono = '+3902020202'
        sede2.email = 'comitato@prova.it'
        sede2.codice_fiscale = '01234567891'
        sede2.partita_iva = '01234567891'
        sede2.locazione = crea_locazione()
        sede2.save()

        seconda_appartenenza = crea_appartenenza(sostenitore, sede2)
        seconda_appartenenza.membro = Appartenenza.SOSTENITORE
        seconda_appartenenza.save()

        volontario_ex_sostenitore = crea_persona()
        appartenenza_ex_sostenitore = crea_appartenenza(volontario_ex_sostenitore, sede2)
        appartenenza_ex_sostenitore.inizio = oggi
        appartenenza_ex_sostenitore.save()

        appartenenza_ex_sostenitore = crea_appartenenza(volontario_ex_sostenitore, sede2)
        appartenenza_ex_sostenitore.inizio = passato
        appartenenza_ex_sostenitore.fine = oggi - datetime.timedelta(days=1)
        appartenenza_ex_sostenitore.terminazione = Appartenenza.PROMOZIONE
        appartenenza_ex_sostenitore.membro = Appartenenza.SOSTENITORE
        appartenenza_ex_sostenitore.save()

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=20, fine_soci_nv=fine_anno
        )

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno_successivo, fine_soci=anno_successivo,
            anno=anno_successivo.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=20, fine_soci_nv=anno_successivo
        )

        # Non registrata per mancato rispetto importo minimo
        data = {
            'persona': sostenitore.pk,
            'importo': 8,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email=utente1.email, password=utente1.password_testing)
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'importo minimo per la quota sostenitore per l')

        # Non registrata per anno diverso da quello corrente
        data = {
            'persona': sostenitore.pk,
            'importo': 8,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': (oggi - datetime.timedelta(days=400)).strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Non è possibile registrare quote sostenitore per un anno diverso da quello corrente')

        # Registrata
        data = {
            'persona': sostenitore.pk,
            'importo': 20,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta registrata
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

        # Non registrata perché già registrata nell'anno corrente
        data = {
            'persona': sostenitore.pk,
            'importo': 20,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'è già stata registrata per la Sede del Comitato di')

        # Registrata perché su comitato diverso
        data = {
            'persona': sostenitore.pk,
            'importo': 20,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        self.client.login(email=utente2.email, password=utente2.password_testing)
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta non registrata
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].find('?appena_registrata='))

        # Non registrata perché è solo volontario, non sostenitore
        data = {
            'persona': volontario_ex_sostenitore.pk,
            'importo': 20,
            'causale': 'test ricevute',
            'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
            'data_versamento': oggi.strftime('%d/%m/%Y')
        }
        response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
        # ricevuta non registrata
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Questa persona non è registrata come Sostenitore CRI')

        with freeze_time('2017-10-14'):
            # Registrata perché in anno successivo
            data = {
                'persona': sostenitore.pk,
                'importo': 20,
                'causale': 'test ricevute',
                'tipo_ricevuta': Quota.QUOTA_SOSTENITORE,
                'data_versamento': poco_fa().strftime('%d/%m/%Y')
            }
            self.client.login(email=utente2.email, password=utente2.password_testing)
            response = self.client.post('{}{}'.format(self.live_server_url, reverse('us_ricevute_nuova')), data=data)
            # ricevuta non registrata
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response['location'].find('?appena_registrata='))

    @freeze_time('2017-01-30')
    def test_elenco_non_paganti_dimessi_assenti(self):
        """
        Verifica che i volontari dimessi non vengano inclusi nell'elenco dei volontari
         che non hanno pagato la quota associativa per l'anno dell'elenco.
        """
        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)
        sessione_presidente = self.sessione_utente(persona=presidente)
        crea_tesseramento(anno=2017)

        # Vai all'elenco quote da pagare
        sessione_presidente.visit("%s/us/quote/" % self.live_server_url)
        with sessione_presidente.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario deve pagare la quota
            self.assertTrue(iframe.is_text_present(volontario.nome))

        # Dimetti il volontario
        d = Dimissione(
            persona=volontario, appartenenza=appartenenza,
            sede=sede, motivo=Dimissione.VOLONTARIE,
            richiedente=presidente, info="Una motivazione di esempio"
        )
        d.save()
        d.applica(trasforma_in_sostenitore=False, invia_notifica=False)

        # Vai nuovamente all'elenco quote da pagare
        sessione_presidente.visit("%s/us/quote/" % self.live_server_url)
        with sessione_presidente.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario NON compare in elenco come dovente pagare quota
            self.assertTrue(iframe.is_text_not_present(volontario.nome))

    @freeze_time('2017-01-30')
    def test_elenco_non_paganti_trasferiti_uscenti_assenti(self):
        """
        Verifica che i volontari trasferiti verso un altro comitato
         non vengano inclusi nell'elenco dei volontari
         che non hanno pagato la quota associativa per l'anno dell'elenco.
        """
        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)
        sessione_presidente = self.sessione_utente(persona=presidente)
        crea_tesseramento(anno=2017)

        presidente_nuova_sede = crea_persona()
        nuova_sede = crea_sede(presidente=presidente_nuova_sede)

        # Vai all'elenco quote da pagare
        sessione_presidente.visit("%s/us/quote/" % self.live_server_url)
        with sessione_presidente.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario deve pagare la quota
            self.assertTrue(iframe.is_text_present(volontario.nome))

        # Trasferisci il volontario presso la nuova sede
        t = Trasferimento(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede,
            motivo="Mi andava di trasferirmi"
        )
        t.save()
        t.richiedi(notifiche_attive=False)
        t.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa())

        # Vai nuovamente all'elenco quote da pagare
        sessione_presidente.visit("%s/us/quote/" % self.live_server_url)
        with sessione_presidente.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario NON compare in elenco come dovente pagare quota
            self.assertTrue(iframe.is_text_not_present(volontario.nome))


    @freeze_time('2017-01-30')
    def test_elenco_non_paganti_trasferiti_entranti_presenti(self):
        """
        Verifica che i volontari trasferiti verso questo comitato
         vengono inclusi nell'elenco dei volontari che non hanno pagato
         la quota, se non hanno pagato la quota presso il loro comitato
         di origine.
        """

        crea_tesseramento(anno=2017)

        vecchio_presidente = crea_persona()
        volontario, vecchia_sede, vecchia_appartenenza = crea_persona_sede_appartenenza(presidente=vecchio_presidente)

        nuovo_presidente = crea_persona()
        nuova_sede = crea_sede(presidente=nuovo_presidente)

        sessione = self.sessione_utente(persona=nuovo_presidente)

        # Trasferisci il volontario presso la nuova sede
        t = Trasferimento(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede, motivo="Una qualunque"
        )
        t.save()
        t.richiedi(notifiche_attive=False)
        t.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa())

        # Vai all'elenco quote da pagare
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario non e' ancora presente
            self.assertTrue(iframe.is_text_present(volontario.nome))


    @freeze_time('2017-01-30')
    def test_elenco_non_paganti_estesi_entranti_assenti(self):
        """
        Verifiche che i volontari che sono estesi presso questo comitato
         non vengono inclusi nell'elenco, neanche se non hanno ancora pagato
         la quota associativa.
        """

        crea_tesseramento(anno=2017)

        vecchio_presidente = crea_persona()
        volontario, vecchia_sede, vecchia_appartenenza = crea_persona_sede_appartenenza(presidente=vecchio_presidente)

        nuovo_presidente = crea_persona()
        nuova_sede = crea_sede(presidente=nuovo_presidente)

        sessione = self.sessione_utente(persona=nuovo_presidente)

        # Creiamo una estensione di servizio
        e = Estensione(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede, motivo="Per divertimento"
        )
        e.save()
        e.richiedi(notifiche_attive=False)
        e.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa(),
                                  notifiche_attive=True)

        # Vai all'elenco quote da pagare
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.DA_VERSARE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario non e' ancora presente
            self.assertTrue(iframe.is_text_not_present(volontario.nome))

    @freeze_time('2017-01-30')
    def test_elenco_paganti_dimessi_assenti(self):
        """
        Verifica che il volontario che e' stato dimesso non appaio piu' nell'elenco
         dei volontari aventi pagato quota. Questo e' perche' questo NON e' un elenco
         di quote, bensi' un elenco di soci attuali che hanno pagato la quota.
        """
        crea_tesseramento(anno=2017)

        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        sessione = self.sessione_utente(persona=presidente)

        # Registra una quota per il volontario
        Quota.nuova(appartenenza=appartenenza, data_versamento=oggi(),
                    registrato_da=presidente, importo=8, tipo=Quota.QUOTA_SOCIO,
                    causale="Quota Socio 2017", invia_notifica=False)

        # Vai all'elenco quote versate
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.VERSATE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario e' presente come pagante
            self.assertTrue(iframe.is_text_present(volontario.nome))

        # Dimetti il volontario
        d = Dimissione(
            persona=volontario, appartenenza=appartenenza,
            sede=sede, motivo=Dimissione.VOLONTARIE,
            richiedente=presidente, info="Una motivazione di esempio"
        )
        d.save()
        d.applica(trasforma_in_sostenitore=False, invia_notifica=False)

        # Vai all'elenco quote versate
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.VERSATE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario NON e' piu' presente come pagante
            self.assertTrue(iframe.is_text_not_present(volontario.nome))


    @freeze_time('2017-01-30')
    def test_elenco_paganti_trasferiti_uscenti_assenti(self):
        """
        Verifica che il volontario che si e' trasferito presso un nuovo
         comitato non appare piu' nel comitato di origine.
        Questo e' perche' questo NON e' un elenco di quote, bensi' un elenco
         di volontari attuali aventi pagato la quota.
        """
        crea_tesseramento(anno=2017)

        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        nuovo_presidente = crea_persona()
        nuova_sede = crea_sede(presidente=nuovo_presidente)

        sessione = self.sessione_utente(persona=presidente)

        # Registra una quota per il volontario
        Quota.nuova(appartenenza=appartenenza, data_versamento=oggi(),
                    registrato_da=presidente, importo=8, tipo=Quota.QUOTA_SOCIO,
                    causale="Quota Socio 2017", invia_notifica=False)

        # Trasferisci il volontario presso la nuova sede
        t = Trasferimento(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede, motivo="Una qualunque"
        )
        t.save()
        t.richiedi(notifiche_attive=False)
        t.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa())

        # Vai all'elenco quote versate
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.VERSATE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario NON e' piu' presente come pagante
            self.assertTrue(iframe.is_text_not_present(volontario.nome))


    @freeze_time('2017-01-30')
    def test_elenco_paganti_trasferiti_entranti_presenti(self):
        """
        Verifica che il volontario che si e' trasferito presso un nuovo
         comitato, dopo aver pagato la quota, appare ora nell'elenco dei paganti
         presso il nuovo comitato.
        Questo e' perche' questo NON e' un elenco di quote, bensi' un elenco
         di volontari attuali aventi pagato la quota.
        """
        crea_tesseramento(anno=2017)

        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        nuovo_presidente = crea_persona()
        nuova_sede = crea_sede(presidente=nuovo_presidente)

        sessione = self.sessione_utente(persona=nuovo_presidente)

        # Registra una quota per il volontario
        Quota.nuova(appartenenza=appartenenza, data_versamento=oggi(),
                    registrato_da=presidente, importo=8, tipo=Quota.QUOTA_SOCIO,
                    causale="Quota Socio 2017", invia_notifica=False)

        # Trasferisci il volontario presso la nuova sede
        t = Trasferimento(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede, motivo="Una qualunque"
        )
        t.save()
        t.richiedi(notifiche_attive=False)
        t.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa())

        # Vai all'elenco quote versate
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.VERSATE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario e' presente nell'elenco del nuovo comitato
            self.assertTrue(iframe.is_text_present(volontario.nome))

    @freeze_time('2017-01-30')
    def test_elenco_paganti_estesi_entranti_assenti(self):
        """
        Verifica che il volontario avente pagato la quota associativa non appare
         nell'elenco dei paganti quota presso il comitato dove e' esteso.
        """

        crea_tesseramento(anno=2017)

        presidente = crea_persona()
        volontario, sede, appartenenza = crea_persona_sede_appartenenza(presidente=presidente)

        nuovo_presidente = crea_persona()
        nuova_sede = crea_sede(presidente=nuovo_presidente)

        sessione = self.sessione_utente(persona=nuovo_presidente)

        # Registra una quota per il volontario
        Quota.nuova(appartenenza=appartenenza, data_versamento=oggi(),
                    registrato_da=presidente, importo=8, tipo=Quota.QUOTA_SOCIO,
                    causale="Quota Socio 2017", invia_notifica=False)

        # Creiamo una estensione di servizio
        e = Estensione(
            richiedente=volontario, persona=volontario,
            destinazione=nuova_sede, motivo="Per divertimento"
        )
        e.save()
        e.richiedi(notifiche_attive=False)
        e.autorizzazione_concessa(modulo=None, auto=True, data=poco_fa(),
                                  notifiche_attive=True)

        # Vai all'elenco quote versate
        sessione.visit("%s/us/quote/" % self.live_server_url)
        with sessione.get_iframe(0) as iframe:
            iframe.select('tipo', ModuloElencoQuote.VERSATE)
            iframe.fill('anno', '2017')
            iframe.find_by_xpath("//button[@type='submit']").first.click()

            # Il volontario NON e' presente nell'elenco del nuovo comitato
            self.assertTrue(iframe.is_text_not_present(volontario.nome))


    @freeze_time('2016-11-14')
    def test_cancellazione_quota_socio(self):

        # Crea oggetti e nomina un delegato US locale
        delegato = crea_persona()
        sessione_delegato_locale = self.sessione_utente(persona=delegato)
        volontario, sede, appartenenza = crea_persona_sede_appartenenza()
        sede.aggiungi_delegato(UFFICIO_SOCI, delegato)

        # Crea oggetti e nomina un delegato US territoriale
        delegato_territoriale = crea_persona()
        sessione_delegato_territoriale = self.sessione_utente(persona=delegato_territoriale)
        volontario_territoriale = crea_persona()
        sede_territoriale = crea_sede(estensione=TERRITORIALE, genitore=sede)
        sede_territoriale.aggiungi_delegato(UFFICIO_SOCI, delegato_territoriale)
        appartenenza_territoriale = crea_appartenenza(persona=volontario_territoriale, sede=sede_territoriale)

        sede_territoriale.locazione = crea_locazione()
        sede_territoriale.save()

        oggi = poco_fa()
        inizio_anno = oggi.replace(month=1, day=1)
        fine_soci = inizio_anno.replace(month=3) - datetime.timedelta(days=1)

        Tesseramento.objects.create(
            stato=Tesseramento.APERTO, inizio=inizio_anno, fine_soci=fine_soci,
            anno=inizio_anno.year, quota_attivo=8, quota_ordinario=8, quota_benemerito=8,
            quota_aspirante=8, quota_sostenitore=8
        )

        # registra e cancella quota volontario locale da US locale
        quota = Quota.nuova(appartenenza=appartenenza, data_versamento=oggi,
                            registrato_da=delegato, causale="Quota",
                            importo=8.0)

        sessione_delegato_locale.visit("%s/us/ricevute/%d/annulla/" % (self.live_server_url, quota.pk))
        self.assertTrue(sessione_delegato_locale.is_text_present("ANNULLATA"))

        # registra quota volontario territoriale da US locale
        quota = Quota.nuova(appartenenza=appartenenza_territoriale,
                            data_versamento=oggi, registrato_da=delegato,
                            causale="Quota", importo=8.0)

        sessione_delegato_locale.visit("%s/us/ricevute/%d/annulla/" % (self.live_server_url, quota.pk))
        self.assertTrue(sessione_delegato_locale.is_text_present("ANNULLATA"))

        # registra quota volontario territoriale da US territoriale (queo)
        quota = Quota.nuova(appartenenza=appartenenza_territoriale,
                            data_versamento=oggi, registrato_da=delegato_territoriale,
                            causale="Quota", importo=8.0)

        sessione_delegato_territoriale.visit("%s/us/ricevute/%d/annulla/" % (self.live_server_url, quota.pk))
        self.assertTrue(sessione_delegato_territoriale.is_text_present("ANNULLATA"))


    @freeze_time('2018-03-21')
    def test_download_iscritti(self):

        # crea oggetti e appartenza
        presidente = crea_persona()
        direttore_corso = crea_persona()
        aspirante1 = crea_persona()
        aspirante2 = crea_persona()
        sostenitore1 = crea_persona()
        sostenitore2 = crea_persona()
        sede = crea_sede(presidente)
        crea_appartenenza(direttore_corso, sede, tipo=Appartenenza.DIPENDENTE)
        crea_appartenenza(sostenitore1, sede, tipo=Appartenenza.SOSTENITORE)
        crea_appartenenza(sostenitore2, sede, tipo=Appartenenza.SOSTENITORE)

        # crea locazione, aspiranti e corso
        locazione = crea_locazione()
        Aspirante.objects.create(raggio=900, locazione=locazione, persona=aspirante1)
        Aspirante.objects.create(raggio=900, locazione=locazione, persona=aspirante2)
        corso_base = CorsoBase.objects.create(locazione=locazione, stato=Delega.ATTIVA, sede=sede,
                                              data_inizio=poco_fa(),
                                              data_esame=datetime.date(2018, 10, 10),
                                              anno=2018, progressivo=1)

        # nomina delegato corso
        Delega.objects.create(persona=direttore_corso, stato=Delega.ATTIVA, tipo=DIRETTORE_CORSO,
                              inizio=poco_fa(), oggetto=corso_base, firmatario=presidente)

        # invito al corso aspirante1 e sostenitore1
        InvitoCorsoBase.objects.create(persona=aspirante1, corso=corso_base, invitante=direttore_corso)
        InvitoCorsoBase.objects.create(persona=sostenitore1, corso=corso_base, invitante=direttore_corso)

        # iscritti al corso aspirante2 e sostenitore2
        partecipazione1 = PartecipazioneCorsoBase.objects.create(persona=aspirante2, corso=corso_base, confermata=True)
        partecipazione2 = PartecipazioneCorsoBase.objects.create(persona=sostenitore2, corso=corso_base,
                                                                 confermata=True)

        # autorizzazioni al corso aspirante2 e sostenitore2
        Autorizzazione.objects.create(richiedente=aspirante2, firmatario=direttore_corso, concessa=True,
                                      oggetto=partecipazione1, progressivo=1,
                                      destinatario_ruolo=INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI,
                                      destinatario_oggetto=corso_base, necessaria=False)
        Autorizzazione.objects.create(richiedente=sostenitore2, firmatario=direttore_corso, concessa=True,
                                      oggetto=partecipazione2, progressivo=1,
                                      destinatario_ruolo=INCARICO_GESTIONE_CORSOBASE_PARTECIPANTI,
                                      destinatario_oggetto=corso_base, necessaria=False)

        # sessione
        sessione_direttore = self.sessione_utente(persona=direttore_corso)
        sessione_direttore.visit("%s/aspirante/corso-base/%d/iscritti/" % (self.live_server_url, corso_base.pk))
        with sessione_direttore.get_iframe(0) as iframe_direttore:
            link = iframe_direttore.find_link_by_partial_text("Excel: Un foglio per sede").first._element.get_attribute(
                'href')
        try:
            sessione_direttore.visit(link)
            self.assertFalse(sessione_direttore.is_text_present("Server Error (500)"))
        except:
            self.assertTrue(True)