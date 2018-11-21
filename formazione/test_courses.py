from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse
from base.utils_tests import (crea_persona_sede_appartenenza, crea_persona,
    crea_appartenenza, email_fittizzia, crea_utenza, codice_fiscale, crea_locazione)
from anagrafica.models import *
from formazione.models import *


def create_persona(with_utenza=True):
    persona = crea_persona()
    persona.email_contatto = email_fittizzia()
    persona.codice_fiscale = codice_fiscale()
    persona.save()

    if with_utenza:
        utenza = crea_utenza(persona, persona.email_contatto)
        return persona, utenza
    else:
        return persona

def create_aspirante(sede, persona=None):
    if not persona:
        persona = create_persona()[0]

    a = Aspirante(persona=persona)
    a.locazione = sede.locazione
    a.save()
    return a

def create_course(data_inizio, sede, extension_type=CorsoBase.EXT_MIA_SEDE,
        tipo=Corso.CORSO_NUOVO, **kwargs):

    corso = CorsoBase.nuovo(tipo=tipo, extension_type=extension_type, sede=sede,
        data_inizio=data_inizio, data_esame=data_inizio + timedelta(days=14),
        stato=Corso.ATTIVO, **kwargs)
    corso.locazione = sede.locazione
    corso.save()
    return corso

class TestCorsoNuovo(TestCase):
    def setUp(self):
        """ Create users """
        ### Presidente ###
        self.presidente, self.presidente_utenza = create_persona()
        self.direttore, self.sede, self.appartenenza = crea_persona_sede_appartenenza(
            presidente=self.presidente)

        ### Aspirante ###
        self.aspirante1 = create_aspirante(sede=self.sede)
        self.aspirante2 = create_aspirante(sede=self.sede)

        ### Volontario ###
        self.volontario = None

        """ Create a new courses tipo CORSO_NUOVO """
        data_inizio = datetime.datetime.now() + timedelta(days=14)
        self.c1 = create_course(data_inizio, self.sede) # corso_1_ext_mia_sede
        self.c2 = create_course(data_inizio, self.sede, extension_type=CorsoBase.EXT_LVL_REGIONALE) # corso_2_ext_a_livello_regionale
        self.c3 = create_course(data_inizio, self.sede, tipo=Corso.BASE)

    def test_corso_nuovo_invisible_to_aspirante(self):
        email = self.aspirante1.persona.email_contatto
        login = self.client.login(username=email, password='prova')
        response = self.client.get(reverse('aspirante:corsi_base'))
        ctx = response.context

        ### Asserting ###
        self.assertEqual(str(ctx['user']), email)  # user is logged in
        self.assertEqual(response.status_code, 200)
        self.assertTrue('corsi' in ctx)
        self.assertFalse(self.c1 in ctx['corsi'])  # Nuovo not in ctx
        self.assertFalse(self.c2 in ctx['corsi'])  # Nuovo not in ctx
        self.assertTrue(self.c3 in ctx['corsi'])  # Base in ctx

        # Courses can access to
        c3 = self.c3
        response = self.client.get(reverse('aspirante:info', args=[c3.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, c3.nome, status_code=200)

        # Courses can not access to
        response = self.client.get(reverse('aspirante:info', args=[self.c1.pk]))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('aspirante:info', args=[self.c2.pk]))
        self.assertEqual(response.status_code, 302)

    def test_corso_nuovo_visible_to_volunteer(self):
        pass

    def test_corso_nuovo_extensions_link_visible_only_for_corso_nuovo(self):
        pass