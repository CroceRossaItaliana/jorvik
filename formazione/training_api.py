import requests
from django.conf import settings
from requests import PreparedRequest

from autenticazione.models import Utenza
from jorvik.settings import MOODLE_KEY, MOODLE_DOMAIN


class TrainingApi:
    token = ''
    domain = ''
    pr = None

    DIRETTORE = 1
    DISCENTE = 5

    def __init__(self):
        self.pr = PreparedRequest()
        self.token = MOODLE_KEY
        self.domain = MOODLE_DOMAIN

    def core_course_get_courses_by_field_shortname(self, shortname):

        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "core_course_get_courses_by_field",
                "field": "shortname",
                "value": shortname
            }
        )
        return r['courses'][0]

    def core_user_get_users_by_field(self, email):

        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "core_user_get_users_by_field",
                "field": "email",
                "values[0]": email
            }
        )
        return r[0] if r else r

    def core_user_create_users(self, persona):

        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "core_user_create_users",
                "users[0][username]": persona.email,
                "users[0][password]": Utenza.objects.get(persona=persona).password,
                "users[0][firstname]": persona.nome,
                "users[0][lastname]": persona.cognome,
                "users[0][email]": persona.email,
            }
        )

        return r[0] if r else r

    def core_role_assign_roles(self, userid, contextid, roleid):
        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "core_role_assign_roles",
                "assignments[0][roleid]": roleid,
                "assignments[0][userid]": userid,
                "assignments[0][contextid]": contextid
            }
        )

        return r

    def enrol_manual_enrol_users(self, userid, contextid, roleid):
        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "enrol_manual_enrol_users",
                "enrolments[0][roleid]": roleid,
                "enrolments[0][userid]": userid,
                "enrolments[0][courseid]": contextid
            }
        )
        return r

    def enrol_manual_unenrol_users(self, userid, contextid, roleid):
        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "enrol_manual_unenrol_users",
                "enrolments[0][roleid]": roleid,
                "enrolments[0][userid]": userid,
                "enrolments[0][courseid]": contextid
            }
        )
        return r

    def cancellazione_iscritto(self, persona, corso):
        utente = self.core_user_get_users_by_field(persona.email)
        corso = self.core_course_get_courses_by_field_shortname(corso.titolo_cri.nome)

        return self.enrol_manual_unenrol_users(utente['id'], corso['id'], self.DISCENTE)

    def aggiugi_ruolo(self, persona, corso, ruolo):
        utente = self.core_user_get_users_by_field(persona.email)
        corso = self.core_course_get_courses_by_field_shortname(corso.titolo_cri.nome)
        # Se l'utente non esiste lo crea
        if not utente:
            utente = self.core_user_create_users(persona)

        if ruolo == self.DIRETTORE:
            return self.core_role_assign_roles(utente['id'], corso['id'], ruolo)
        elif ruolo == self.DISCENTE:
            return self.enrol_manual_enrol_users(utente['id'], corso['id'], ruolo)

    def tool_lp_data_for_user_competency_summary_in_course(self, userid, competencyid, courseid):
        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "tool_lp_data_for_user_competency_summary_in_course",
                "userid": userid,
                "competencyid": competencyid,
                "courseid": courseid
            }
        )
        return r

    def core_competency_list_course_competencies(self, courseid):
        r = self._get(
            url=self.domain,
            parameters={
                "moodlewsrestformat": "json",
                "wstoken": self.token,
                "wsfunction": "core_competency_list_course_competencies",
                "id": courseid
            }
        )
        return r

    def ha_ottenuto_competenze(self, persona, corso):
        utente = self.core_user_get_users_by_field(persona.email)
        corso = self.core_course_get_courses_by_field_shortname(corso.titolo_cri.nome)
        competencies_id = [competencie['competency']['id'] for competencie in self.core_competency_list_course_competencies(corso['id'])]
        ha_ottenuto = False
        for id in competencies_id:
            competencie = self.tool_lp_data_for_user_competency_summary_in_course(
                utente['id'],
                id,
                corso['id']
            )
            ha_ottenuto = True if competencie else False
        return ha_ottenuto

    def _get(self, url, parameters=None, headers=None, data=None):

        if data is None:
            data = {}
        if headers is None:
            headers = {}
        if parameters is None:
            parameters = {}

        self.pr.prepare_url(url, parameters)

        r = requests.get(self.pr.url, headers=headers, data=data)

        return r.json()
