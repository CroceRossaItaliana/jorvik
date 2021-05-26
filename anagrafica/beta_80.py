import json
import requests
from http import client
from django.conf import settings

from anagrafica.models import Persona, Delega, Sede
from anagrafica.permessi.costanti import DELEGATO_AREA, RESPONSABILE_AREA

import logging
logger = logging.getLogger(__name__)


class Beta80Api:

    SCOPE = {
        DELEGATO_AREA: 'OPT',
        RESPONSABILE_AREA: 'RESP'
    }

    def __init__(self, bearer=None):
        self.bearer = bearer
        super().__init__()

    def _scope(self, tipo_delega='', sede_id=None):
        delega = self.SCOPE.get(tipo_delega, '')
        return "CRI.CT.CT_{}.{}".format(sede_id, delega)

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
            "SubjectId": persona.utenza.pk,
            "UserName": persona.utenza.email,
            "FirstName": persona.nome,
            "LastName": persona.cognome,
            "Email": persona.email,
            "ClientId": "CUSCRI",
            "IsActive": "Y"
        }

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/User/Save'),
            headers=self._headers(),
            data=json.dumps(payload)
        )

        if request.status_code in [client.OK, client.CREATED]:
            logger.info(
                "{} SubjectId: {} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, '/BO/api/v1/identitymanager/bo/User/Save', request.status_code
                )
            )
            return request.json()
        else:
            logger.warning(
                "{} SubjectId: {} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, '/BO/api/v1/identitymanager/bo/User/Save', request.status_code
                )
            )
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None

    def set_scope_user(self, persona: Persona, tipo_delega='', sede_id=None):
        scope = self._scope(tipo_delega=tipo_delega, sede_id=sede_id)
        payload = {
            "SubjectId": persona.utenza.pk,
            "Code": scope,
            "ClientId": "CUSCRI",
        }

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/UserScopes/Save'),
            headers=self._headers(),
            data=json.dumps(payload)
        )

        if request.status_code in [client.OK, client.CREATED]:
            logger.info(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/UserScopes/Save', request.status_code
                )
            )
            return request.json()
        else:
            logger.warning(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/UserScopes/Save', request.status_code
                )
            )
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None

    def delete_scope_user(self, persona: Persona, tipo_delega='', sede_id=None):
        scope = self._scope(tipo_delega=tipo_delega, sede_id=sede_id)
        payload = {
            "SubjectId": persona.utenza.pk,
            "Code": scope,
            "ClientId": "CUSCRI",
        }

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/UserScopes/Delete'),
            headers=self._headers(),
            data=json.dumps(payload)
        )

        if request.status_code in [client.OK, client.CREATED]:
            logger.info(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/UserScopes/Delete', request.status_code
                )
            )
            return request.json()
        else:
            logger.warning(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/UserScopes/Delete', request.status_code
                )
            )
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None


    def user_delete(self, persona: Persona, tipo_delega='', sede_id=None):
        scope = self._scope(tipo_delega=tipo_delega, sede_id=sede_id)
        payload = {
            "SubjectId": persona.utenza.pk,
            "ClientId": "CUSCRI",
            "Code": scope
        }

        request = requests.post(
            '{}{}'.format(settings.BETA_80_HOST, '/BO/api/v1/identitymanager/bo/User/Delete'),
            headers=self._headers(),
            data=json.dumps(payload)
        )

        if request.status_code in [client.OK, client.CREATED]:
            logger.info(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/User/Delete', request.status_code
                )
            )
            return request.json()
        else:
            logger.warning(
                "{} SubjectId: {} Code:{} url: {} status_code: {}".format(
                    persona, persona.utenza.pk, scope, '/BO/api/v1/identitymanager/bo/User/Delete', request.status_code
                )
            )
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None
