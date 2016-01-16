import datetime

from django.test import TestCase

from anagrafica.models import Appartenenza, Sede, Persona
from base.utils_tests import crea_persona_sede_appartenenza, crea_persona, crea_sede, crea_appartenenza
from ufficio_soci.elenchi import ElencoElettoratoAlGiorno
from ufficio_soci.forms import ModuloElencoElettorato


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


