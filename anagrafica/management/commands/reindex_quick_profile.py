from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from anagrafica.models import Persona
from curriculum.models import Titolo
from jorvik.settings import STATIC_PROD_BASEURL, ELASTIC_HOST, ELASTIC_QUICKPROFILE_INDEX
from ufficio_soci.models import Tesserino


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = []
        persone = Persona.objects.all()
        done = 0
        for pp in persone:
            payload = {'_id': pp.id, 'nome': pp.nome, 'cognome': pp.cognome, 'sospeso': pp.sospeso,
                       'codice_fiscale': pp.codice_fiscale, 'data_nascita': str(pp.data_nascita),
                       'avatar': STATIC_PROD_BASEURL + pp.avatar.url if pp.avatar else None, 'donatore': {}}

            if hasattr(pp, 'donatore'):
                payload['donatore'] = dict(gruppo_sanguigno=pp.donatore.gruppo_sanguigno,
                                           fattore_rh=pp.donatore.fattore_rh,
                                           fenotipo_rh=pp.donatore.fenotipo_rh)

            payload['tesserino'] = []
            try:
                tesserini = Tesserino.objects.filter(valido=True, persona=pp.id)

                for tesserino in tesserini:
                    if tesserino.codice:
                        payload['tesserino'].append(tesserino.codice)

            except ObjectDoesNotExist as e:
                payload['tesserino'] = []

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

        url = "{}/{}/_doc/".format(ELASTIC_HOST, ELASTIC_QUICKPROFILE_INDEX)

        headers = {
            'Content-Type': 'application/json'
        }

        for d in data:
            _id = d.pop('_id')
            response = requests.request("POST", url + str(_id), headers=headers, json=d, verify=False)
            print(response.text)
            done += 1

        print('done: {}'.format(done))
