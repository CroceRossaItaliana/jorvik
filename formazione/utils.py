from collections import OrderedDict
from datetime import datetime

from django.db.models import Q

from anagrafica.costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from base.utils import CalendarTemplate
from curriculum.areas import OBBIETTIVI_STRATEGICI
from curriculum.models import Titolo


def costruisci_titoli(context={}, qs=None, search_query='', key=''):
    for i in OBBIETTIVI_STRATEGICI:
        area_id, area_nome = i
        areas = qs.filter(area=i[0])

        context[key][area_nome] = OrderedDict()

        for k in Titolo.CDF_LIVELLI:
            level_id = k[0]
            levels = areas.filter(cdf_livello=level_id)
            context[key][area_nome]['level_%s' % level_id] = levels

        if search_query:
            # Fare pulizia dei settori che non hanno un risultato (solo nel caso di ricerca)
            settore_in_dict = context[key][area_nome]
            cleaned = OrderedDict((a,t) for a,t in dict(settore_in_dict).items() if t)
            if not len(cleaned):
                del context[key][area_nome]
            else:
                context[key][area_nome] = cleaned

    return context


class CalendarCorsi(CalendarTemplate):

    BACKGROUND_COLOR = {
        NAZIONALE: ('#FF3333', '#ffffff'), # ROSSO - BIANCO
        REGIONALE: ('#4C9900', '#ffffff'), # VERDE - BIANCO
        PROVINCIALE: ('#00CCCC', '#ffffff'), # AZZURRO - BIANCO
        LOCALE: ('#FF9323', '#ffffff'), # ARANCIONE - BIANCO
        TERRITORIALE: ('#FF9323', '#ffffff'), # VIOLA - BIANCO
    }

    def __init__(self, date, corsi):
        self.year = date.year
        self.month = date.month
        self.corsi = corsi
        super().__init__(date)

    def formatday(self, day):
        a = ""

        if day == 0:
            return '<td></td>'

        # 1: Trova turni con l'inizio questo gg, questo mese
        corsi_per_giorno = self.corsi.filter(Q(data_inizio__day=day),
                                             data_inizio__month=self.month)

        # 2: Memorizza i suoi numeri
        pk_tmp = list(corsi_per_giorno.values_list('pk', flat=True))

        # 3: Ulteriore ricerca dei turni che hanno inizio prima o dopo questo mese
        for turno in self.corsi:
            d = datetime(self.year, self.month, day)
            if turno.data_inizio <= d <= turno.data_esame:
                # 4. Memorizza anche questi turni
                pk_tmp.append(turno.pk)

        # 5. Query tutti turni insieme
        corsi_per_giorno = self.corsi.filter(pk__in=pk_tmp)

        for corso in corsi_per_giorno:
            if corso.titolo_cri:
                a += "<a data-toggle='tooltip' data-placement='top' title='%s' target='_blank' style='background-color: %s; color: %s' href='%s'>%s</a>" % (
                    '{} - {}'.format(corso.nome, corso.sede),
                    self.BACKGROUND_COLOR[corso.sede.estensione][0],
                    self.BACKGROUND_COLOR[corso.sede.estensione][1],
                    corso.url,
                    corso.titolo_cri.sigla
                )
            else:
                a += "<a data-toggle='tooltip' data-placement='top' title='%s' target='_blank' style='background-color: %s; color: %s' href='%s'>%s</a>" % (
                    '{} - {}'.format(corso.nome, corso.sede),
                    self.BACKGROUND_COLOR[corso.sede.estensione][0],
                    self.BACKGROUND_COLOR[corso.sede.estensione][1],
                    corso.url,
                    'CRI'
                )

        return """<td>
        <span class='date'>%s</span> 
            <div class='so-calendar__day-items'>
                %s
            </div>
        </td>""" % (day, a)
