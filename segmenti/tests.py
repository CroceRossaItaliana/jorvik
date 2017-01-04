# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from datetime import timedelta

from django.test import TestCase

from anagrafica.models import Appartenenza, Persona
from base.utils import poco_fa
from base.utils_tests import crea_persona, crea_persona_sede_appartenenza
from segmenti.segmenti import volontari_piu_un_anno, volontari_meno_un_anno


class TestSegmenti(TestCase):

    def test_segmento_anzianita(self):

        meno_di_tre_anni_fa = poco_fa() - timedelta(days=360*3)
        meno_di_due_anni_fa = poco_fa() - timedelta(days=360*2)
        meno_di_un_anno_fa = poco_fa() - timedelta(days=360)

        presidente = crea_persona()
        persona_1 = crea_persona()
        persona_2 = crea_persona()
        persona_3 = crea_persona()
        presidente, sede, _ = crea_persona_sede_appartenenza(presidente)

        Appartenenza.objects.create(
            persona=persona_1,
            sede=sede,
            membro=Appartenenza.VOLONTARIO,
            inizio=meno_di_tre_anni_fa,
            confermata=True
        )

        Appartenenza.objects.create(
            persona=persona_2,
            sede=sede,
            membro=Appartenenza.VOLONTARIO,
            inizio=meno_di_due_anni_fa,
            confermata=True
        )

        Appartenenza.objects.create(
            persona=persona_3,
            sede=sede,
            membro=Appartenenza.VOLONTARIO,
            inizio=meno_di_un_anno_fa,
            confermata=True
        )

        meno_di_un_anno = volontari_meno_un_anno(Persona.objects.all())
        self.assertEqual(meno_di_un_anno.count(), 1)
        self.assertEqual(meno_di_un_anno.get(), persona_3)

        meno_di_due_anni = volontari_piu_un_anno(Persona.objects.all())
        self.assertEqual(meno_di_due_anni.count(), 3)
        self.assertTrue(presidente in meno_di_due_anni)
        self.assertTrue(persona_1 in meno_di_due_anni)
        self.assertTrue(persona_2 in meno_di_due_anni)
