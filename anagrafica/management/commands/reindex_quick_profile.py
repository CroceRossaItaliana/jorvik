import json
from pprint import pprint

import requests

from django.core.management import BaseCommand
from anagrafica.models import Persona
from anagrafica.serializers import CurriculumPersonaSerializer
from curriculum.models import Titolo
from jorvik.settings import ELASTIC_HOST, ELASTIC_CURRICULUM_INDEX


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = []
        persone = Persona.objects.filter(id__gte=201000)[:10000]

        for pp in persone:
            payload = {}
            payload['nome'] = pp.nome
            payload['cognome'] = pp.cognome
            payload['sospeso'] = pp.sospeso

            _patenti = []
            for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.PATENTE_CIVILE):
                _patenti.append(dict(tipo=dict(Titolo.TIPO)[Titolo.PATENTE_CIVILE],
                                     data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza)))

            _titoli_cri = []
            for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.TITOLO_CRI):
                _titoli_cri.append(dict(tipo=dict(Titolo.TIPO)[Titolo.TITOLO_CRI],
                                     data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza)))

            _altri_titoli = []
            for _ in pp.titoli_personali.filter(titolo__tipo=Titolo.ALTRI_TITOLI):
                _altri_titoli.append(dict(tipo=dict(Titolo.TIPO)[Titolo.ALTRI_TITOLI],
                                     data_ottenimento=str(_.data_ottenimento), data_scadenza=str(_.data_scadenza)))

            payload['patenti'] = _patenti
            payload['titoli_cri'] = _titoli_cri
            payload['altri_titoli'] = _altri_titoli

            data.append(payload)

        import requests
        import json

        url = "https://es.staging.gaia.cri.it/quick_profile.dev/_doc"

        headers = {
            'Content-Type': 'application/json'
        }

        for d in data:
            response = requests.request("POST", url, headers=headers, json=d, verify=False)
            print(response.text)

