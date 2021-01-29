import io
import csv
import xlsxwriter

from django.db import models
from django.http import HttpResponse
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
        lezioni_sheet = {}

        united_list = list()

        risposte = SurveyResult.objects.filter(course=course)
        for num, result in enumerate(risposte):

            response_json = OrderedDict(result.response_json)

            direttori = sorted(response_json.get('direttori').items())
            utilita_lezioni = sorted(response_json.get('utilita_lezioni').items())
            # org_servizi = response_json.get('org_servizi')
            lezioni = response_json.get('lezioni').items()

            # LEZIONI
            if lezioni:
                lezioni_dict_new = dict()
                for docente_pk, lezioni in lezioni:
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
                    for docente, lezione in sorted(lezioni_dict_new.items()):
                        for l, questions in lezione.items():
                            for question, voto in questions.items():
                                if l.nome not in lezioni_sheet:
                                    lezioni_sheet[l.nome] = {'domande': [question.text], 'risposte': {}, 'medie': {}}
                                else:
                                    lezioni_sheet[l.nome]['domande'].append(question.text)
                    is_intestazione_lezioni = True

                # Recupero risposte per lezioni per ogni docente
                for docente, lezione in sorted(lezioni_dict_new.items()):
                    for l, questions in lezione.items():
                        for question, voto in questions.items():
                            if str(docente) not in lezioni_sheet[l.nome]['risposte']:
                                lezioni_sheet[l.nome]['risposte'][str(docente)] = [voto]
                            else:
                                lezioni_sheet[l.nome]['risposte'][docente].append(voto)

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
                                    'value': int(risposta),
                                    'count': 1
                                }
                            else:
                                medie_direttori[str(col_direttore)]['value'] += int(risposta)
                                medie_direttori[str(col_direttore)]['count'] += 1
                        worksheet_direttori.write(row_direttore, col_direttore, risposta)
                        col_direttore += 1

        for name_sheet, obj in lezioni_sheet.items():
            worksheet_lezione = workbook.add_worksheet(name_sheet[:30])
            worksheet_lezione.write(0, 0, name_sheet, bold)
            col_lezioni = 1
            row_lezioni = 1
            media_lezione = []
            # Intestazione
            for intestazione in obj['domande']:
                media_lezione.append(0)
                worksheet_lezione.write(row_lezioni, col_lezioni, intestazione, bold)
                col_lezioni += 1
            col_lezioni = 1
            row_lezioni += 1
            # Docenti e Voti
            count = 0
            for docente, voti in obj['risposte'].items():
                worksheet_lezione.write(row_lezioni, 0, docente, bold)
                index = 0
                for voto in voti:
                    media_lezione[index] += int(voto)
                    worksheet_lezione.write(row_lezioni, col_lezioni, voto)
                    col_lezioni += 1
                    index += 1
                col_lezioni = 1
                row_lezioni += 1
                count += 1

            row_lezioni += 1
            worksheet_lezione.write(row_lezioni, 0, 'Medie', bold)

            # Medie
            for media in media_lezione:
                if media:
                    worksheet_lezione.write(row_lezioni, col_lezioni, round(media/count))
                col_lezioni += 1

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


        # TODO: grafici
        # value_chat = '=Grafici!$0$1'
        # worksheet_grafici = workbook.add_worksheet('Grafici')
        # worksheet_grafici.write_column('A1', [1, 2, 3])
        #
        # chart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})
        # chart.add_series({'values': ['Grafici', 0, 0, 2, 0]})
        # chart.add_series({'values': ['Grafici', 0, 1, 0, 1]})
        # chart.add_series({'values': ['Grafici', 0, 2, 0, 2]})

        # worksheet_grafici.insert_chart(10, 3, chart)



            # if utilita_lezioni:
            #     for lezione_pk, risposta in utilita_lezioni.items():
            #         if lezione_pk not in united['utilita_lezioni']:
            #             united['utilita_lezioni'][lezione_pk] = list()
            #         united['utilita_lezioni'][lezione_pk].append(risposta)

            # if org_servizi:
            #     for question_pk, risposta in org_servizi.items():
            #         if question_pk not in united['org_servizi']:
            #             united['org_servizi'][question_pk] = list()
            #         united['org_servizi'][question_pk].append(risposta)
            #
            # if lezioni:
            #     united['lezioni'] = list()
            #     for docente_pk, lezione in lezioni.items():
            #         for k, v in lezione.items():
            #             if docente_pk.isalpha() or '_' in docente_pk:
            #                 docente = docente_pk
            #             else:
            #                 docente = Persona.objects.get(pk=docente_pk).nome_completo
            #
            #             v.pop('completed')
            #
            #             for lez in sorted(v.items()):
            #                 domanda = Question.objects.get(pk=lez[0])
            #                 lezione_col = [domanda.text, lez[1]]
            #
            #                 united['lezioni'].append(lezione_col + [docente])

            # org_servizi_columns = [[Question.objects.get(pk=k).text] + [i for i in v] for k, v in united['org_servizi'].items()]
            #
            # utilita_lezioni_columns = list()
            # for lezione_pk, v in united['utilita_lezioni'].items():
            #     if not LezioneCorsoBase.objects.filter(pk=lezione_pk).count():
            #         continue
            #     utilita_lezioni_columns.append([LezioneCorsoBase.objects.get(pk=lezione_pk).nome] + [i for i in v])
            #
            # united['org_servizi'] = org_servizi_columns
            # united['utilita_lezioni'] = utilita_lezioni_columns
            #
            # # Valorizzazione campi (nomi direttori)
            # nomi_direttori_columns = ["Chi era il tuo Direttore di Corso?"]
            # direttori_domande_columns = dict()
            #
            # for direttore_pk, voti in united['direttori'].items():
            #     # Calcolare lunghezza delle risposte e moltiplicare il nome
            #     len_voti = len(voti.values())
            #     p = [Persona.objects.get(pk=direttore_pk).nome_completo] * len_voti
            #     nomi_direttori_columns.extend(p)
            #
            #     for domanda_pk, v in voti.items():
            #         domanda = Question.objects.get(pk=domanda_pk).text
            #         if domanda not in direttori_domande_columns:
            #             direttori_domande_columns[domanda] = list()
            #         direttori_domande_columns[domanda].append(v)
            #         q = [None for i in range(len_voti)]
            #         q.pop(0)
            #         direttori_domande_columns[domanda].extend(q)
            #
            # united['direttori'] = [[k] + v for k,v in direttori_domande_columns.items()]
            #
            # united_list.append(united)
            #
            # # Inserimento prima colonna (nomi direttori)
            # for col, data in enumerate([nomi_direttori_columns], 0):
            #     worksheet.write_column(0, 0, data)

        # row = 0
        # for line, united in enumerate(united_list):
        #     col = 1
        #     row_tmp = 0
        #
        #     for section_name, values in united.items():
        #         if not len(values):
        #             continue
        #
        #         for data in values:
        #             if section_name == 'direttori':
        #                 data = list(filter(bool, data))
        #
        #             if section_name == 'lezioni':
        #                 domanda, voto, docente = data
        #                 data = [domanda, docente, voto]
        #
        #             if line != 0:
        #                 data = [data[-1:][0]]
        #
        #             worksheet.write_column(row, col, data)
        #             col += 1
        #         else:
        #             row_tmp = len(data)
        #     row += row_tmp

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
