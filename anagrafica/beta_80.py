from enum import Enum
import requests
from http import client
from django.conf import settings

from anagrafica.models import Persona, Delega
from anagrafica.permessi.costanti import DELEGATO_AREA, RESPONSABILE_AREA


class Beta80Api:

    SCOPE = {
        DELEGATO_AREA: 'OPER',
        RESPONSABILE_AREA: 'MANAGER'
    }

    bearer = None

    def __init__(self):
        super().__init__()

    def _scope(self, delega: Delega):
        delega = self.SCOPE.get(delega.tipo, None)
        return "CRI.CT.CT_{}.{}".format(str(delega.oggetto.sede.id), delega)

    def _headers(self, **kwargs):
        headers = {
            'Content-Type': 'application/json'
        }

        if self.bearer:
            headers['Authorization'] = 'Bearer {}'.format(self.bearer)

        headers.update(kwargs)

        return headers

    def insert_or_update_user(self, persona: Persona):
        payload = {
            "SubjectId": persona.pk,
            "UserName": persona.utenza.email,
            "FirstName": persona.nome,
            "LastName": persona.cognome,
            "Email": persona.email
        }

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/User/Save'),
            headers=self._headers(),
            payload=payload
        )

        return request.json() if request.status_code in [client.OK, client.CREATED] else None

    def set_scope_user(self, persona: Persona, delega: Delega):
        pass

    def list_user_by_committee(self):
        pass

    def user_delete(self):

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/User/Delete'),
            headers=self._headers(),
        )

        return request.json() if request.status_code in [client.OK, client.CREATED] else None

    def get_user_by_subject_id(self, subject_id: str):
        pass
