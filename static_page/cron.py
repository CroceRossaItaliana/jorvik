from collections import OrderedDict
import datetime
import requests

from django.conf import settings
from django.db.models import Q

from anagrafica.models import Persona, Sede
from anagrafica.permessi.applicazioni import PRESIDENTE, COMMISSARIO, RESPONSABILE_FORMAZIONE, DELEGATO_AREA
from static_page.models import TypeFormCompilati
from static_page.monitoraggio import TypeFormCompilatiCheck

from django_cron import CronJobBase, Schedule


class CronTypeformCompilati(CronJobBase):

    RUN_EVERY_MINS = 30  # every 30 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'static_page.get_compiled_typeforms'  # a unique code

    TYPEFORM_DOMAIN = "https://api.typeform.com"
    TYPEFORM_TOKEN = settings.TOKEN_TYPE_FORM
    ENDPOINT = TYPEFORM_DOMAIN + "/forms/%s"
    HEADERS = {
        'Authorization': "Bearer %s" % TYPEFORM_TOKEN,
        'Content-Type': 'application/json'
    }

    form_ids_fabbisogni_territoriali = OrderedDict([
        ('ZrgLp6bQ', 'Questionario Fabbisogni Formativi Territoriali'),
    ])
    form_ids_fabbisogni_regionali = OrderedDict([
        ('zW2FMF2Y', 'Questionario Fabbisogni Formativi Regionali'),
    ])
    form_ids_transparenza = OrderedDict([
        ('Jo7AmkVU', 'Questionario Trasparenza L. 124/2017')
    ])

    form_ids_autocontrollo = OrderedDict([
        ('ttOyXCJR', 'A-GOVERNANCE'),
        ('PZvVJIZq', 'B-Personale Dipendente e Volontario'),
        ('p5DlUCLt', 'C-Contabilità'),
        ('o7JfxbE5', 'D-Convenzioni e progetti'),
        ('ZwMX5rsG', 'E-Relazioni esterne, comunicazione, trasparenza'),
    ])

    def make_request(cls, form_id, path='', **kwargs):
        # if doesn't show the data or the page is empty, maybe it has to do with pagination
        # https://developer.typeform.com/responses/walkthroughs/
        url = cls.ENDPOINT % form_id + path + '?page_size=1000&before'
        if kwargs.get('completed') == True and kwargs.get('query'):
            url += '?completed=true'
            url += '&query=%s' % kwargs.get('query')
        response = requests.get(url, headers=cls.HEADERS)
        return response

    def do(self):
        one = datetime.datetime.now()
        for key, value in self.form_ids_fabbisogni_territoriali.items():
            res = self.make_request(form_id=key, path='/responses')
            for el in res.json()['items']:
                typeform_in_db = TypeFormCompilati.objects.filter(
                    Q(comitato=Sede.objects.get(pk=int(el['hidden']['c']))) & Q(tipo=value))
                comitato = TypeFormCompilatiCheck(int(el['hidden']['c']), key, value)

                if not typeform_in_db:
                    compilatore = Persona.objects.get(pk=int(el['hidden']['u']))
                    delegha_list = []
                    deleghe = [a for a in compilatore.deleghe_attuali().filter(
                        tipo__in=[PRESIDENTE, COMMISSARIO, RESPONSABILE_FORMAZIONE])]
                    for ogni_delegha in deleghe:
                        if ogni_delegha.oggetto_id == int(el['hidden']['c']):
                            delegha_list.append(ogni_delegha)

                    TypeFormCompilati.objects.create(
                        tipo=value,
                        comitato=Sede.objects.get(pk=int(el['hidden']['c'])),
                        persona=compilatore,
                        delega=delegha_list[0].get_tipo_display() if len(delegha_list) else '---------------',
                        results=comitato._retrieve_data()
                    )
        for key, value in self.form_ids_fabbisogni_regionali.items():
            res = self.make_request(form_id=key, path='/responses')
            for el in res.json()['items']:
                typeform_in_db = TypeFormCompilati.objects.filter(
                    Q(comitato=Sede.objects.get(pk=int(el['hidden']['c']))) & Q(tipo=value))
                comitato = TypeFormCompilatiCheck(int(el['hidden']['c']), key, value)
                if not typeform_in_db:
                    compilatore = Persona.objects.get(pk=int(el['hidden']['u']))
                    delegha_list = []
                    deleghe = [a for a in compilatore.deleghe_attuali().filter(
                        tipo__in=[PRESIDENTE, COMMISSARIO, RESPONSABILE_FORMAZIONE])]
                    for ogni_delegha in deleghe:
                        if ogni_delegha.oggetto_id == int(el['hidden']['c']):
                            delegha_list.append(ogni_delegha)

                    TypeFormCompilati.objects.create(
                        tipo=value,
                        comitato=Sede.objects.get(pk=int(el['hidden']['c'])),
                        persona=compilatore,
                        delega=delegha_list[0].get_tipo_display() if len(delegha_list) else '---------------',
                        results=comitato._retrieve_data()
                    )
        for key, value in self.form_ids_transparenza.items():
            res = self.make_request(form_id=key, path='/responses')
            for el in res.json()['items']:
                typeform_in_db = TypeFormCompilati.objects.filter(
                    Q(comitato=Sede.objects.get(pk=int(el['hidden']['c']))) & Q(tipo=value))
                comitato = TypeFormCompilatiCheck(int(el['hidden']['c']), key, value)
                if not typeform_in_db:
                    compilatore = Persona.objects.get(pk=int(el['hidden']['u']))
                    delegha_list = []
                    deleghe = [a for a in compilatore.deleghe_attuali().filter(
                        tipo__in=[PRESIDENTE, COMMISSARIO, DELEGATO_AREA])]
                    for ogni_delegha in deleghe:
                        if ogni_delegha.oggetto_id == int(el['hidden']['c']):
                            delegha_list.append(ogni_delegha)

                    TypeFormCompilati.objects.create(
                        tipo=value,
                        comitato=Sede.objects.get(pk=int(el['hidden']['c'])),
                        persona=compilatore,
                        delega=delegha_list[0].get_tipo_display() if len(delegha_list) else '---------------',
                        results=comitato._retrieve_data()
                    )

        comitati_compilati_list = []
        for key, value in self.form_ids_autocontrollo.items():
            res = self.make_request(form_id=key, path='/responses')
            for el in res.json()['items']:
                comitati_compilati_list.append(int(el['hidden']['c']))

        from collections import Counter
        comitati_list = []
        for k, v in Counter(comitati_compilati_list).items():
            if v >= 5:
                comitati_list.append(k)

        for key, value in self.form_ids_autocontrollo.items():
            res = self.make_request(form_id=key, path='/responses')
            for el in res.json()['items']:
                if int(el['hidden']['c']) in comitati_list:
                    typeform_in_db = TypeFormCompilati.objects.filter(
                        Q(comitato=Sede.objects.get(pk=int(el['hidden']['c']))) & Q(
                            tipo='Monitoragio Autocontollo'))
                    if not typeform_in_db:
                        comitato = TypeFormCompilatiCheck(int(el['hidden']['c']), key, value)
                        compilatore = Persona.objects.get(pk=int(el['hidden']['u']))

                        delegha_list = []
                        deleghe = [a for a in compilatore.deleghe_attuali().filter(
                            tipo__in=[PRESIDENTE, COMMISSARIO, DELEGATO_AREA])]
                        for ogni_delegha in deleghe:
                            if ogni_delegha.oggetto_id == int(el['hidden']['c']):
                                delegha_list.append(ogni_delegha)

                        TypeFormCompilati.objects.create(
                            tipo='Monitoragio Autocontollo',
                            comitato=Sede.objects.get(pk=int(el['hidden']['c'])),
                            persona=compilatore,
                            delega=delegha_list[0].get_tipo_display() if len(delegha_list) else '---------------',
                            results=comitato._retrieve_data()
                        )
        finish = datetime.datetime.now()
        print('It took: "%s" to run this script......................' % (finish - one))
