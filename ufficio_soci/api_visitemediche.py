import json
import logging
import re
import requests
from http import client
from django.conf import settings
logger = logging.getLogger(__name__)


class VisiteMedicheApi:

    def __init__(self):
        headers = {
            'Authorization': settings.VISITEMEDICHE_AUTH,
        }
        data = {
            'grant_type': 'client_credentials'
        }

        response = requests.post(
            '{}/token'.format(settings.VISITEMEDICHE_HOST),
            headers=headers, data=data, verify=True
        )
        if response.status_code in [client.OK, client.CREATED]:
            token = response.json()
            self.bearer = token['access_token']

            logger.info(
                "Bearer loaded: url {} status_code: {}".format(
                    '/token', response.status_code
                )
            )
        else:
            logger.warning(
                "Bearer not loaded: url: {} status_code: {}".format(
                    '/token', response.status_code
                )
            )
        super().__init__()
    
    def _headers(self, **kwargs):
        headers = {
            'Content-Type': 'application/json'
        }

        if self.bearer:
            headers['Authorization'] = 'Bearer {}'.format(self.bearer)

        headers.update(kwargs)

        return headers

    @property
    def examination_types(self):
        request = requests.get(
            '{}/public/cri/medicalexamination/examination/type/list'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers()
        )
        
        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/type/list'))
            logger.warning("response: {}".format(request.text))
            return []
    
    @property
    def examination_status(self):
        request = requests.get(
            '{}/public/cri/medicalexamination/examination/status/list'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers()
        )
        
        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/status/list'))
            logger.warning("response: {}".format(request.text))
            return []
    
    def committee_doctors_list(self, committeeId, numpage=0):
        """ lista dei medici associati al comitato
        """
        request = requests.get(
            '{}/public/cri/medicalexamination/doctor/committee?page={}&committeeId={}'.format(
                settings.VISITEMEDICHE_HOST, numpage, committeeId
            ),
            headers=self._headers()
        )
        
        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/doctor/commitee'))
            logger.warning("payload: committeId={}".format(committeeId))
            logger.warning("response: {}".format(request.text))
            return None

    def doctors_list(self, committeeId=None, numpage=0):
        """ lista dei medici associabili al comitato
        """
        if (committeeId):
            request = requests.get(
                '{}/public/cri/medicalexamination/doctor/list?page={}&excludeCommitteeId={}'.format(
                    settings.VISITEMEDICHE_HOST, numpage, committeeId
                ),
                headers=self._headers()
            )
        else:
            request = requests.get(
                '{}/public/cri/medicalexamination/doctor/list?page={}'.format(
                    settings.VISITEMEDICHE_HOST, numpage
                ),
                headers=self._headers()
            )

        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/doctor/list'))
            logger.warning("payload: committeId={}".format(committeeId))
            logger.warning("response: {}".format(request.text))
            return None

    def associate_doctor_committee(self, doctorUuid, committeeId):

        payload = {
            "doctorUuid": doctorUuid,
            "committeeId": committeeId
        }

        request = requests.post(
            '{}/public/cri/medicalexamination/doctor/committee'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers(),
            data=json.dumps(payload)
        )

        if request.status_code == 200:
            return request.status_code
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/doctor/committee'))
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None
    
    def deassociate_doctor_committee(self, associateId):

        request = requests.delete(
            '{}/public/cri/medicalexamination/doctor/committee/{}'.format(
                settings.VISITEMEDICHE_HOST, associateId
            ),
            headers=self._headers() 
        )

        if request.status_code == 200:
            return request.status_code
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/doctor/committee/{}'.format(associateId)))
            logger.warning("response: {}".format(request.text))
            return None

    def patient_examination(self, patientId, numpage=0):

        payload = {
            "patientId": patientId,
            "page": numpage
        }

        request = requests.get(
            '{}/public/cri/medicalexamination/examination/list'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers(),
            params=payload,
        )
        
        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/list'))
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None

    def search_examination(self, committeeId, doctorUuid=None, statusId=None, date=None, numpage=0):

        payload = {
            "committeeId": committeeId,
            "page": numpage
        }

        if doctorUuid:
            payload['doctorUuid'] = doctorUuid
        if statusId:
            payload['statusId'] = statusId
        if date:
            payload['date'] = date

        request = requests.get(
            '{}/public/cri/medicalexamination/examination/list'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers(),
            params=payload,
        )
        
        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/list'))
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None

    def get_examination_doctor(self, doctorID):
        request = requests.get(
            '{}/public/cri/medicalexamination/doctor/{}'.format(
                settings.VISITEMEDICHE_HOST, doctorID
            ),
            headers=self._headers()
        )

        if request.status_code == 200:
            return request.json()
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/doctor/{}'.format(doctorID)))
            logger.warning("response: {}".format(request.text))
            return None

    def remove_examination(self, examinationID):
        request = requests.put(
            '{}/public/cri/medicalexamination/examination/remove/{}'.format(
                settings.VISITEMEDICHE_HOST, examinationID
            ),
            headers=self._headers(),
            data=json.dumps({})
        )

        if request.status_code == 200:
            return request.status_code
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/{}'.format(examinationID)))
            logger.warning("response: {}".format(request.text))
            return None

    def add_examination(self, committeeId, doctorId, personId, examinationTypeId, date):

        payload = {
            "exStartAt": date,
            "exDoctorUuid": doctorId,
            "exIdPatientExt": personId,
            "exCalendarId": None,
            "exStatusId": 1,
            "exExpireAt": None,
            "exExaminationTypeId": examinationTypeId,
            "committeeId": committeeId,
        }

        request = requests.post(
            '{}/public/cri/medicalexamination/examination/'.format(
                settings.VISITEMEDICHE_HOST
            ),
            headers=self._headers(),
            data=json.dumps(payload)
        )
  
        if request.status_code == 200:
            return request.status_code
        else:
            logger.warning("call: {}".format(
                'public/cri/medicalexamination/examination/'))
            logger.warning("payload: {}".format(json.dumps(payload)))
            logger.warning("response: {}".format(request.text))
            return None
