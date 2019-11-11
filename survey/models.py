from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.postgres.fields import JSONField

from anagrafica.models import Persona


class Survey(models.Model):
    FORMAZIONE = 'f'
    SURVEY_TYPE_CHOICES = (
        (FORMAZIONE, 'Formazione'),
    )

    is_active = models.BooleanField(default=True)
    text = models.CharField(max_length=255)
    survey_type = models.CharField(max_length=3, choices=SURVEY_TYPE_CHOICES,
                                   null=True, blank=True)

    def get_questions(self):
        return self.question_set.all()

    def get_my_responses(self, user, course):
        return SurveyResult.objects.filter(survey=self, user=user, course=course)

    def get_responses_dict(self, me, course):
        d = dict()
        for r in self.get_my_responses(me, course):
            qid = r.question.qid
            if qid not in d:
                d[qid] = dict(response=r.response, object=r)
        return d

    def is_course_admin(self, me, course):
        from anagrafica.permessi.costanti import MODIFICA
        return me and me.permessi_almeno(course, MODIFICA)

    def can_vote(self, me, course):
        """
        Cannot vote because is not participant of the course
        or the course is not ended yet.
        """
        if self.is_course_admin(me, course):
            return True
        elif me in [p.persona for p in course.partecipazioni_confermate()]:
            if course.concluso:
                return True
        return False

    def has_user_responses(self, course):
        return SurveyResult.get_responses_for_course(course).exists()

    @classmethod
    def survey_for_corso(cls):
        try:
            return cls.objects.get(id=2)
        except Survey.DoesNotExist:
            s = cls.objects.filter(survey_type=cls.FORMAZIONE, is_active=True)
            return s.last() if s.exists() else None

    class Meta:
        verbose_name = 'Questionario di gradimento'
        verbose_name_plural = 'Questionari di gradimento'

    def __str__(self):
        return str(self.text)


class Question(models.Model):
    TEXT = 'text'
    RADIO = 'radio'
    SELECT = 'select'
    SELECT_MULTIPLE = 'select-multiple'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'

    QUESTION_TYPES = (
        (TEXT, 'text'),
        (RADIO, 'radio'),
        (SELECT, 'select'),
        (SELECT_MULTIPLE, 'Select Multiple'),
        (INTEGER, 'integer'),
        (BOOLEAN, 'boolean'),
    )

    text = models.CharField(max_length=255)
    survey = models.ForeignKey(Survey)
    is_active = models.BooleanField(default=True)
    required = models.BooleanField(default=True, verbose_name='Obbligatorio')
    order = models.SmallIntegerField(null=True, blank=True)
    question_group = models.ForeignKey('QuestionGroup', null=True, blank=True)
    question_type = models.CharField(max_length=100, choices=QUESTION_TYPES,
                                     default=TEXT, null=True, blank=True)
    anchor = models.CharField(max_length=100, null=True, blank=True)

    @property
    def qid(self):
        return 'qid_%s' % self.pk

    class Meta:
        verbose_name = 'Domanda'
        verbose_name_plural = 'Domande'

    def __str__(self):
        return str(self.text)


class SurveyResult(models.Model):
    from .forms import (QuestionarioPaginaIniziale, SelectDirettoreCorsoForm,
        ValutazioneDirettoreCorsoForm, ValutazioneUtilitaLezioniForm,
        ValutazioneDocenteCorsoForm, ValutazioneOrganizzazioneServiziForm,)

    INIZIO = 'in'
    SELEZIONA_DIRETTORE = 'sd'
    VALUTAZIONE_DIRETTORE = 'vd'
    VALUTAZIONE_LEZIONI = 'vl'
    VALUTAZIONE_DOCENTE = 'dv'
    VALUTAZIONE_ORG_SERVIZI = 'os'
    GRAZIE = 'gr'

    # Not for model field choices use
    STEPS = {
        INIZIO: (0, QuestionarioPaginaIniziale, SELEZIONA_DIRETTORE ),
        SELEZIONA_DIRETTORE: (1, SelectDirettoreCorsoForm, VALUTAZIONE_DIRETTORE),
        VALUTAZIONE_DIRETTORE: (2, ValutazioneDirettoreCorsoForm, VALUTAZIONE_LEZIONI),
        VALUTAZIONE_LEZIONI: (3, ValutazioneUtilitaLezioniForm, VALUTAZIONE_DOCENTE),
        VALUTAZIONE_DOCENTE: (4, ValutazioneDocenteCorsoForm, VALUTAZIONE_ORG_SERVIZI),
        VALUTAZIONE_ORG_SERVIZI: (5, ValutazioneOrganizzazioneServiziForm, GRAZIE),
        GRAZIE: (6, None, None),
    }

    user = models.ForeignKey(Persona)
    course = models.ForeignKey('formazione.CorsoBase', blank=True, null=True)
    survey = models.ForeignKey(Survey)
    question = models.ForeignKey(Question, blank=True, null=True)
    new_version = models.BooleanField(default=False, blank=True)
    response = models.TextField(max_length=1000, blank=True, null=True)
    response_json = JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_responses_for_course(cls, course):
        return cls.objects.filter(course=course)

    @classmethod
    def generate_report_for_course(cls, course):
        import csv
        from django.shortcuts import HttpResponse
        from formazione.models import LezioneCorsoBase

        filename = "Questionario di gradimento [%s].csv" % course.nome
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        writer = csv.writer(response, delimiter=';')

        def _direttori(result):
            rows = list()
            direttori = result.response_json['direttori']
            for persona_pk, response_data in direttori.items():
                p = Persona.objects.get(pk=persona_pk)
                for domanda_pk, risposta in response_data.items():
                    domanda = Question.objects.get(pk=domanda_pk)
                    rows.append([p, domanda.text, risposta])
            return rows

        def _utilita_lezioni_rows(result):
            rows = list()
            utilita_lezioni_rows = result.response_json['utilita_lezioni']
            for lezione_pk, voto in utilita_lezioni_rows.items():
                lezione = LezioneCorsoBase.objects.get(pk=lezione_pk)
                rows.append([lezione.nome, voto])
            return rows

        def _org_servizi(result):
            rows = list()
            org_servizi_rows = result.response_json['org_servizi']
            for domanda_pk, voto in org_servizi_rows.items():
                domanda = Question.objects.get(pk=domanda_pk)
                rows.append([domanda.text, voto])
            return rows

        def _valutazione_docenti(result):
            rows = list()
            lezioni_rows = result.response_json['lezioni']

            for docente_pk, lezione_data in lezioni_rows.items():
                if docente_pk.startswith('de_'):
                    docente = docente_pk
                else:
                    docente = Persona.objects.get(pk=docente_pk)

                for lezione_pk, data in lezione_data.items():
                    lezione = LezioneCorsoBase.objects.get(pk=lezione_pk)

                    for domanda_pk, risposta in data.items():
                        if domanda_pk == 'completed':  continue
                        domanda = Question.objects.get(pk=domanda_pk)

                        rows.append([docente, lezione, domanda, risposta])

            return rows

        # Trova le risposte per il questionario di questo corso
        responses_to_q = cls.get_responses_for_course(course)

        # Verifica se le risposte sono JSON (nuova modalità)
        responses_with_json = responses_to_q.filter(new_version=True)
        if responses_with_json.exists():
            responses_to_q = responses_with_json

            # Report per le risposte in JSON
            columns = [
                '1. Valutazione direttore (nome)', 'Domanda', 'Risposta',
                '2. Utilita lezione', 'Voto',
                '3. Valutazione docente (nome)', 'Lezione', 'Domanda', 'Voto',
                '4. Org. e servizi (domanda)', 'Risposta',
                'Creato', 'Modificato',
            ]

            writer.writerow(columns)
            for result in responses_to_q:
                direttori_rows = _direttori(result)
                utilita_lezioni_rows = _utilita_lezioni_rows(result)
                valutazione_docente_rows = _valutazione_docenti(result)
                org_servizi_rows = _org_servizi(result)

                for row in direttori_rows:
                    writer.writerow(row + [''] * 8 + [result.created_at, result.updated_at])

                for row in utilita_lezioni_rows:
                    writer.writerow([''] * 3 + row + [''] * 6 + [result.created_at, result.updated_at])

                for row in valutazione_docente_rows:
                    writer.writerow([''] * 5 + row + [''] * 2 + [result.created_at, result.updated_at])

                for row in org_servizi_rows:
                    writer.writerow([''] * 9 + row + [result.created_at, result.updated_at])

        else:
            # Report per le risposte vecchio formato (prima del rilascio)
            # Ogni risposta -> record db <SurveyResult>
            columns = ['Corso', 'Domanda', 'Risposta', 'Creato', 'Modificato']
            writer.writerow(columns)

            responses_to_q = responses_to_q.exclude(new_version=True)
            for result in responses_to_q:
                writer.writerow([
                    course.nome,
                    result.question,
                    result.response,
                    result.created_at,
                    result.updated_at
                ])

        return response

    def get_uncompleted_valutazione_docente_lezione(self):
        """
        Restituisce docente -> lezione da valutare (completed=False).
        Restituisce None, None: Se non ci sono gruppo docente->lezione da
        valutare (assenti completed=False).

        :return: docente.pk<int> or None, lezione.pk <int> or None
        """
        docenti = self.response_json['lezioni']
        for docente_pk, lezione_data in docenti.items():
            for lezione_pk, lezione_data in lezione_data.items():
                if lezione_data['completed']:
                    continue

                if docente_pk.startswith('de_'):
                    return docente_pk, int(lezione_pk)
                else:
                    return int(docente_pk), int(lezione_pk)

        return None, None

    @property
    def current_step(self):
        if self.response_json is not None:
            return self.response_json.get('step')
        return None

    @property
    def concluso(self):
        return True if self.current_step == SurveyResult.GRAZIE else False

    @property
    def final_step_id(self):
        return SurveyResult.STEPS[SurveyResult.GRAZIE][0]

    class Meta:
        verbose_name = "Risposta dell'utente"
        verbose_name_plural = "Risposte degli utenti"

    def __str__(self):
        return "%s = %s" % (self.survey, self.user)


class QuestionGroup(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)
