import io
import csv

import xlsxwriter
import re
from django.db import models
from django.http import HttpResponse
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
    def _generate_excel(cls, course):
        from formazione.models import LezioneCorsoBase
        from collections import OrderedDict

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        bold = workbook.add_format({'bold': True})


        # DIRETTORE
        row_direttore = 0
        col_direttore = 0
        is_intestazione_direttore = False
        worksheet_direttori = workbook.add_worksheet('Direttori')
        medie_direttori = OrderedDict()
        '''
            coll_media: {
                value:
                count:
            }
        '''

        # UTILITà lezioni
        worksheet_utilita_lezioni = workbook.add_worksheet('Utilità lezioni')
        row_utilita_lezioni = 0
        col_utilita_lezioni = 1
        is_intestazione_utilita_lezioni = False
        medie_utilita_lezioni = OrderedDict()
        '''
            coll_media: {
                value:
                count:
            }
        '''

        # Lezioni
        is_intestazione_lezioni = False
        intestazione_lezioni = []
        sheet_lezioni = {}

        # Oraganizazione Servizio
        worksheet_org_servizi = workbook.add_worksheet('Oraganizazione Servizio')
        is_intestazione_org_servizi = False
        medie_org_servizi = OrderedDict()
        row_org_servizi = 0
        col_org_servizi = 1
        '''
            coll_media: {
                value:
                count:
            }
        '''

        risposte = SurveyResult.objects.filter(course=course)
        for num, result in enumerate(risposte):

            if result.response_json:
                response_json = OrderedDict(result.response_json)
            else:
                continue

            direttori = sorted(response_json.get('direttori').items())
            utilita_lezioni = sorted(response_json.get('utilita_lezioni').items())
            org_servizi = response_json.get('org_servizi')
            lezioni_dict = response_json.get('lezioni').items()

            # Oraganizazione Servizio
            if org_servizi:
                if not is_intestazione_org_servizi:
                    for domanda_pk, valore in org_servizi.items():
                        worksheet_org_servizi.write(
                            row_org_servizi,
                            col_org_servizi,
                            Question.objects.get(pk=domanda_pk).text,
                            bold
                        )
                        col_org_servizi += 1
                    col_org_servizi = 1
                    row_org_servizi += 1
                    is_intestazione_org_servizi = True

                for domanda_pk, risposta in org_servizi.items():
                    domanda = Question.objects.get(pk=domanda_pk)
                    if domanda.question_type == Question.BOOLEAN:
                        worksheet_org_servizi.write(
                            row_org_servizi,
                            col_org_servizi,
                            'Vero' if risposta else 'Falso'
                        )
                    else:
                        if domanda.question_type == Question.RADIO:
                            if str(col_org_servizi) not in medie_org_servizi:
                                medie_org_servizi[str(col_org_servizi)] = {
                                    'value': int(risposta) if risposta else 0,
                                    'count': 1
                                }
                            else:
                                medie_org_servizi[str(col_org_servizi)]['value'] += int(risposta) if risposta else 0
                                medie_org_servizi[str(col_org_servizi)]['count'] += 1
                        worksheet_org_servizi.write(
                            row_org_servizi,
                            col_org_servizi,
                            risposta
                        )
                    col_org_servizi += 1

                col_org_servizi = 1
                row_org_servizi += 1

            # LEZIONI
            if lezioni_dict:
                lezioni_dict_new = dict()
                for docente_pk, lezioni in lezioni_dict:
                    if docente_pk.isalpha() or '_' in docente_pk:
                        p = docente_pk
                    else:
                        p = Persona.objects.get(pk=docente_pk).nome_completo

                    if p not in lezioni_dict_new:
                        lezioni_dict_new[p] = dict()

                    lezioni_not_existing = list()  # to avoid RuntimeError dictionary size changed
                    lezioni_dict_new[p] = lezioni

                    for lezione_pk in lezioni.keys():
                        if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
                            lezioni_not_existing.append(lezione_pk)

                    lezioni_dict_new[p] = {
                        LezioneCorsoBase.objects.get(pk=lezione_pk): {
                            Question.objects.get(pk=domanda_pk): voto for domanda_pk, voto in v.items() if
                            domanda_pk != 'completed'
                        }
                        for lezione_pk, v in lezioni.items() if lezione_pk not in lezioni_not_existing
                    }

                # INTESTAZIONE LEZIONI
                if not is_intestazione_lezioni:
                    for docente, lezioni in lezioni_dict_new.items():

                        for lezione, domande_risposte in sorted(lezioni.items(), key=lambda x: x[0].pk):

                            for domanda, risposta in sorted(domande_risposte.items(), key=lambda x: x[0].pk):

                                if domanda.text not in intestazione_lezioni:
                                    intestazione_lezioni.append(domanda.text)

                    is_intestazione_lezioni = True

                    # LEZIONI INTESTAZIONE
                    for lezione in course.lezioni.all():

                        nome_lezione = re.sub(r'[\[\]:*?\/\\]*', '', lezione.nome)

                        if nome_lezione not in sheet_lezioni:
                            sheet = workbook.add_worksheet(nome_lezione[:30])
                            sheet_lezioni[nome_lezione] = {
                                'sheet': sheet,
                                'coll': 1,
                                'row': 1,
                                'medie': OrderedDict()
                            }
                            sheet.write(0, 0, nome_lezione, bold)
                            for intestazione in intestazione_lezioni:
                                sheet.write(
                                    sheet_lezioni[nome_lezione]['row'],
                                    sheet_lezioni[nome_lezione]['coll'],
                                    intestazione,
                                    bold
                                )
                                sheet_lezioni[nome_lezione]['coll'] += 1

                            sheet_lezioni[nome_lezione]['coll'] = 1
                            sheet_lezioni[nome_lezione]['row'] += 1

                for docente, lezioni in lezioni_dict_new.items():

                    for lezione, domande_risposte in sorted(lezioni.items(), key=lambda x: x[0].pk):
                        nome_lezione = re.sub(r'[\[\]:*?\/\\]*', '', lezione.nome)

                        for domanda, risposta in sorted(domande_risposte.items(), key=lambda x: x[0].pk):
                            sheet_lezione = sheet_lezioni[nome_lezione]
                            if sheet_lezioni[nome_lezione]['coll'] == 1:
                                sheet_lezione['sheet'].write(
                                    sheet_lezioni[nome_lezione]['row'],
                                    0,
                                    docente,
                                    bold
                                )
                            sheet_lezione['sheet'].write(
                                sheet_lezioni[nome_lezione]['row'],
                                sheet_lezioni[nome_lezione]['coll'],
                                risposta
                            )
                            if sheet_lezioni[nome_lezione]['coll'] not in sheet_lezione['medie']:
                                sheet_lezione['medie'][sheet_lezioni[nome_lezione]['coll']] = {
                                    'value': int(risposta) if risposta else 0,
                                    'count': 1
                                }
                            else:
                                sheet_lezione['medie'][sheet_lezioni[nome_lezione]['coll']]['value'] += int(risposta) if risposta else 0
                                sheet_lezione['medie'][sheet_lezioni[nome_lezione]['coll']]['count'] += 1

                            sheet_lezioni[nome_lezione]['coll'] += 1

                        sheet_lezioni[nome_lezione]['coll'] = 1
                        sheet_lezioni[nome_lezione]['row'] += 1

            # Utilità lezioni
            if utilita_lezioni:
                # Aggiungere intestazione Generale
                if not is_intestazione_utilita_lezioni:

                    lezioni_not_existing = list()
                    for lezione_pk, voto in utilita_lezioni:
                        if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
                            lezioni_not_existing.append(lezione_pk)

                    intestazione_utilita_lezioni = [
                        LezioneCorsoBase.objects.get(pk=k).nome for k, v in utilita_lezioni
                        if k not in lezioni_not_existing
                    ]

                    for intestazione in intestazione_utilita_lezioni:
                        worksheet_utilita_lezioni.write(row_utilita_lezioni, col_utilita_lezioni, intestazione, bold)
                        col_utilita_lezioni += 1
                    is_intestazione_utilita_lezioni = True
                    row_utilita_lezioni += 1

                # Aggiungere voti utilità lezioni
                col_utilita_lezioni = 1
                lezioni_not_existing = list()
                for lezione_pk, voto in utilita_lezioni:
                    if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
                        lezioni_not_existing.append(lezione_pk)

                for k, v in utilita_lezioni:
                    if k not in lezioni_not_existing:
                        if str(col_utilita_lezioni) not in medie_utilita_lezioni:
                            medie_utilita_lezioni[str(col_utilita_lezioni)] = {
                                'value': int(v),
                                'count': 1
                            }
                        else:
                            medie_utilita_lezioni[str(col_utilita_lezioni)]['value'] += int(v)
                            medie_utilita_lezioni[str(col_utilita_lezioni)]['count'] += 1
                        worksheet_utilita_lezioni.write(row_utilita_lezioni, col_utilita_lezioni, v)
                        col_utilita_lezioni += 1
                row_utilita_lezioni += 1


            # DIRETTORI
            if direttori:
                # Aggiungere intestazione Direttore
                if not is_intestazione_direttore:
                    intestazione_direttore = [
                        Question.objects.get(pk=domanda_pk).text
                        for direttore_pk, voti in sorted(response_json.get('direttori').items())
                        for domanda_pk, risposta in voti.items()
                    ]

                    # Nome direttore
                    worksheet_direttori.write(
                        row_direttore, col_direttore, course.direttori_corso().first().nome_completo,
                        bold
                    )
                    col_direttore += 1
                    row_direttore += 1
                    # Domande direttore
                    for intestazione in intestazione_direttore:
                        worksheet_direttori.write(row_direttore, col_direttore, intestazione, bold)
                        col_direttore += 1
                    is_intestazione_direttore = True


                # Aggiungere voti direttore
                for direttore_pk, voti in sorted(response_json.get('direttori').items()):
                    items = voti.items()
                    if items:
                        col_direttore = 1
                        row_direttore += 1
                    for domanda_pk, risposta in items:
                        domanda = Question.objects.get(pk=domanda_pk)
                        if domanda.question_type == Question.RADIO and risposta:
                            if str(col_direttore) not in medie_direttori:
                                medie_direttori[str(col_direttore)] = {
                                    'value': int(risposta) if risposte else 0,
                                    'count': 1
                                }
                            else:
                                medie_direttori[str(col_direttore)]['value'] += int(risposta) if risposte else 0
                                medie_direttori[str(col_direttore)]['count'] += 1
                        worksheet_direttori.write(row_direttore, col_direttore, risposta)
                        col_direttore += 1

        # LEZIONI MEDIE
        for nome, obj in sheet_lezioni.items():
            obj['sheet'].write(obj['row']+2, 0, 'Media', bold)
            for col, media in obj['medie'].items():
                obj['sheet'].write(obj['row']+2, col, round(media['value']/media['count'], 1))

        # MEDIE Utilitò Lezioni
        row_utilita_lezioni += 2
        worksheet_utilita_lezioni.write(row_utilita_lezioni, 0, 'Media', bold)
        for col, value in medie_utilita_lezioni.items():
            worksheet_utilita_lezioni.write(row_utilita_lezioni, int(col), round(value['value']/value['count'], 1))

        # MEDIE DIRETTORI
        row_direttore += 2
        worksheet_direttori.write(row_direttore, 0, 'Media', bold)
        for col, value in medie_direttori.items():
            worksheet_direttori.write(row_direttore, int(col), round(value['value']/value['count'], 1))

        # MEDIE ORGANIZZAZIONE SERVIZI
        row_org_servizi += 2
        worksheet_org_servizi.write(row_org_servizi, 0, 'Media', bold)
        for col, value in medie_org_servizi.items():
            worksheet_org_servizi.write(row_direttore, int(col), round(value['value'] / value['count'], 1))


        # GRAFICI
        worksheet_grafici = workbook.add_worksheet('Grafici')

        # GRAFICI Direttore
        chart_direttori = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

        worksheet_grafici.write(0, 0,  'Direttore', bold)
        chart_direttori.add_series(
            {
                'name': [worksheet_direttori.name, 0, 0],
                'categories': [worksheet_direttori.name, 1, 1, 1, 8],
                'values': [worksheet_direttori.name, row_direttore, 1, row_direttore, 8],
                'data_labels': {'series_name': True, 'value': True},
            }
        )
        worksheet_grafici.insert_chart(1, 0, chart_direttori, {'x_scale': 3, 'y_scale': 1})

        # GRAFICI Utilitò Lezioni
        worksheet_grafici.write(20, 0, 'Utilità Lezioni', bold)
        chart_utilita_lezioni = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})
        chart_utilita_lezioni.add_series(
            {
                'categories': [worksheet_utilita_lezioni.name, 0, 1, 1, 15],
                'values': [worksheet_utilita_lezioni.name, row_utilita_lezioni, 1, row_utilita_lezioni, 8],
                'data_labels': {'series_name': True, 'value': True},
            }
        )
        worksheet_grafici.insert_chart(21, 0, chart_utilita_lezioni, {'x_scale': 3, 'y_scale': 1})

        # GRAFICI Organizazioni Servizi
        worksheet_grafici.write(38, 0, 'Organizazioni Servizi', bold)
        chart_org_servizi = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

        chart_org_servizi.add_series(
            {
                'categories': [worksheet_org_servizi.name, 0, 1, 1, 11],
                'values': [worksheet_org_servizi.name, row_org_servizi, 1, row_org_servizi, 11],
                'data_labels': {'series_name': True, 'value': True},
            }
        )
        worksheet_grafici.insert_chart(39, 0, chart_org_servizi, {'x_scale': 3, 'y_scale': 1})

        # GRAFICI Lezioni
        worksheet_grafici.write(55, 0, 'Lezioni', bold)
        chart_lezioni = workbook.add_chart({'type': 'bar'})

        for nome, obj in sheet_lezioni.items():
            chart_lezioni.add_series(
                {
                    'name': [obj['sheet'].name, 0, 0],
                    'categories': [obj['sheet'].name, 1, 1, 1, 4],
                    'values': [obj['sheet'].name, obj['row']+2, 1, obj['row']+2, 4],
                    'data_labels': {'series_name': True, 'value': True},
                }
            )
        worksheet_grafici.insert_chart(56, 0, chart_lezioni, {'x_scale': 3, 'y_scale': 2})

        worksheet_grafici.write(55, 0, 'Lezioni', bold)

        # MEDIA PER LEZIONE
        worksheet_grafici.write(87, 0, 'Media per lezione', bold)
        col = 1

        for nome, obj in sheet_lezioni.items():
            somma = 0
            index = 0
            for _, media in obj['medie'].items():
                somma += media['value'] / media['count']
                index += 1
            worksheet_grafici.write(88, col, nome)
            if index != 0:
                worksheet_grafici.write(
                    89,
                    col,
                    round(somma/index, 1)
                )
            col += 1

        # GRAFICI MEDIA PER LEZIONE
        chart_per_lezioni = workbook.add_chart({'type': 'pie'})
        chart_per_lezioni.add_series(
            {
                # 'name': ['Grafici', 77, 0],
                'categories': ['Grafici', 88, 1, 88, len(sheet_lezioni.keys())],
                'values': ['Grafici', 89, 1, 89, len(sheet_lezioni.keys())],
                'data_labels': {'series_name': True, 'value': True},
            }
        )
        worksheet_grafici.insert_chart(92, 0, chart_per_lezioni, {'x_scale': 3, 'y_scale': 2})

        workbook.close()
        output.seek(0)

        filename = 'Questionario-di-gradimento.xlsx'
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

    @classmethod
    def _generate_pdf(cls, course):
        from io import BytesIO
        from xhtml2pdf import pisa
        from django.http import HttpResponse
        from django.template.loader import render_to_string

        risposte = SurveyResult.objects.filter(course=course)

        html = render_to_string('pdf_questionario.html', {
            'risposte': risposte,
        }).encode('utf-8')

        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html), result, encoding='UTF-8')
        converted = result.getvalue() if not pdf.err else ''

        filename = 'Questionario-di-gradimento.pdf'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response.write(converted)
        return response

    @classmethod
    def _process_and_generate(cls, course, request):
        if 'excel' in request.GET:
            return cls._generate_excel(course)

        elif 'pdf' in request.GET:
            return cls._generate_pdf(course)

        return HttpResponse('No Data')

    @classmethod
    def _process_and_generate_old(cls, course, responses_to_q):
        filename = "Questionario-di-gradimento.csv"
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename

        # Report per le risposte vecchio formato (prima del rilascio)
        # Ogni risposta -> record db <SurveyResult>
        columns = ['Corso', 'Domanda', 'Risposta', 'Creato', 'Modificato']

        writer = csv.writer(response, delimiter=';')
        writer.writerow(columns)

        for result in responses_to_q.exclude(new_version=True):
            writer.writerow([
                course.nome,
                result.question,
                result.response,
                result.created_at,
                result.updated_at
            ])

        return response

    @classmethod
    def get_report_for_course(cls, course, request):
        # Trova le risposte per il questionario di questo corso
        responses_to_q = cls.get_responses_for_course(course)

        # Verifica se le risposte sono JSON (nuova modalità)
        responses_with_json = responses_to_q.filter(new_version=True)
        if responses_with_json.exists():
            return cls._process_and_generate(course, request)
        else:
            return cls._process_and_generate_old(course, responses_to_q)

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
