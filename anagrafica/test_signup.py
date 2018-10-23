import random, names
from datetime import datetime

from django import test

import codicefiscale

from base.comuni import COMUNI
from .models import Persona


class RegistrazioneTest(test.TestCase):
    def test_new_registered_gender_is_set(self):
        genere_list = ['M', 'F']
        for genere in genere_list:
            nome = names.get_first_name()
            cognome = names.get_last_name()
            nascita = datetime(random.randint(1960, 1990),
                               random.randint(1, 12),
                               random.randint(1, 28))
            p = Persona(
                nome=nome,
                cognome=cognome,
                data_nascita=nascita,
                codice_fiscale=codicefiscale.build(nome, cognome, nascita, genere, 'D969'),
                comune_nascita=random.sample(COMUNI.keys(), 1)[0],
                indirizzo_residenza='Via Prova, 34',
                comune_residenza=random.sample(COMUNI.keys(), 1)[0],
                provincia_residenza='EE',
                cap_residenza='00100',)
            p.save()
            self.assertEquals(p.genere_codice_fiscale, genere)
            self.assertEquals(p.genere, genere)
