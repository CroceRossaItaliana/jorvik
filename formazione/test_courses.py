from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse
from base.utils_tests import (crea_persona, crea_utenza, codice_fiscale,
    email_fittizzia, crea_persona_sede_appartenenza, crea_appartenenza,
    crea_locazione)
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

def create_delega():
    """ required for course directors """
    return


def create_volunteer():
    # create appartenenza
    return


def create_extension():
    return


def create_extensions_for_course(course):
    return


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

        """ Create titles """

        """ Create extensions """

    def _login_as(self, email, password='prova'):
        self.client.login(username=email, password=password)

    def test_corso_nuovo_invisible_to_aspirante(self):
        email = self.aspirante1.persona.email_contatto
        login = self._login_as(self.aspirante1.persona.email_contatto)
        response = self.client.get(reverse('aspirante:corsi_base'))
        ctx = response.context

        ### Asserting ###
        self.assertEqual(str(ctx['user']), email)  # user is logged in
        self.assertEqual(response.status_code, 200)
        self.assertTrue('corsi' in ctx)
        self.assertFalse(self.c1 in ctx['corsi'])  # Nuovo excluded
        self.assertFalse(self.c2 in ctx['corsi'])  # Nuovo excluded
        self.assertTrue(self.c3 in ctx['corsi'])  # CorsoBase in list of courses

    def test_aspirante_have_access_to_corso_base(self):
        c3 = self.c3
        login = self._login_as(self.aspirante1.persona.email_contatto)
        response = self.client.get(reverse('aspirante:info', args=[c3.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, c3.nome, status_code=200)

    def test_aspirante_no_access_to_corso_nuovo(self):
        login = self._login_as(self.aspirante1.persona.email_contatto)

        response = self.client.get(reverse('aspirante:info', args=[self.c1.pk]))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('aspirante:info', args=[self.c2.pk]))
        self.assertEqual(response.status_code, 302)

    def test_corso_nuovo_visible_to_volunteer(self):
        pass

    def test_corso_nuovo_extensions_link_visible_only_for_corso_nuovo(self):
        pass

    def test_volunteer_has_required_titles(self):
        pass
        """
        has all titles
        not all titles
        """

    def test_volunteer_available_courses_listing(self):
        pass

    def test_volunteer_can_participate_at_course(self):
        pass

    def test_corso_nuovo_new_fields_on_modify_page(self):
        pass

    def test_corso_nuovo_fields_visible_only_for_corso_nuovo(self):
        pass

    def test_corso_nuovo_extensions(self):
        pass
        """
        1) CAN list course: [user titles == corso ext titles (all required)] + [
        user sede in corso ext sede]
        2) CAN list course: corso has only sede without titles, user sede in 
        corso sede
        """

    def test_corso_nuovo_extensions_sede(self):
        pass
        """
        user app. sede in course extensions sede 
        """

    def test_corso_nuovo_extensions_sede_expanded(self):
        pass
        """
        - user appartenenza sede is in courses' extensions expanded sede
        - 1st extension has sedi_sottostanti, 2nd extension not, user's sede 
        is in one of them.
        - user app. sede is not in course extensions sede (corso non visible)
        """

    def test_volunteer_listing_course_found_by_firmatario_sede(self):
        pass
        """
        if CorsoBase.extension_type = MIA_SEDE
        user app sede == firmatario_sede
        """

    def test_method_corsobase_has_extensions(self):
        # self.assertTrue(c2.has_extensions())
        pass

    def test_method_persona_has_required_titles_for_course(self):
        pass

    def test_method_corsobase_get_extensions(self):
        pass

    def test_method_corsobase_get_extensions_sede(self):
        pass

    def test_method_corsobase_get_extensions_titles(self):
        pass

    def test_method_corsobase_get_volunteers_by__(self):
        pass
        """
        c.get_extensions_titles()
        c.get_volunteers_by_course_requirements()
        c.get_volunteers_by_only_sede()
        c.get_volunteers_by_ext_sede()
        c.get_volunteers_by_ext_titles()
        """

    def test_course_activated_volunteers_informed(self):
        pass

    def test_property_is_corso_nuovo(self):
        self.assertTrue(self.c1.is_nuovo_corso)
        self.assertTrue(self.c2.is_nuovo_corso)
        self.assertFalse(self.c3.is_nuovo_corso)

    def test_field_extension_type(self):
        self.assertEqual(self.c1.extension_type, CorsoBase.EXT_MIA_SEDE)
        self.assertEqual(self.c2.extension_type, CorsoBase.EXT_LVL_REGIONALE)
        self.assertEqual(self.c3.extension_type, CorsoBase.EXT_MIA_SEDE)

    def test_termina_corso_nuovo(self):
        pass

    def test_termina_corso_titolo_cri_is_set_to_volunteers(self):
        pass
