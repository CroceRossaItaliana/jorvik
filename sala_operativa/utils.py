from datetime import datetime, timedelta, date
from collections import OrderedDict
from calendar import HTMLCalendar, monthrange

from django.db.models import Q

from anagrafica.permessi.costanti import GESTIONE_SO_SEDE, GESTIONE_SERVIZI


def unique(items):
    found = set([])
    keep = list()

    for item in items:
        if item not in found:
            found.add(item)
            keep.append(item)

    return keep


def turni_raggruppa_giorno(qs_turni):
    """
    Da un elenco di turni (queryset), li raggruppa per giorno.
    NB: Questo effettua l'evaluation del queryset.
    :param qs_turni: I turni.
    :return:
    """
    giorni = unique([i.inizio.date() for i in qs_turni])
    risultato = OrderedDict([(d, []) for d in giorni])
    for d in giorni:
        for i in qs_turni:
            if i.inizio.date() == d:
                risultato[d].append(i)
    return risultato


def visibilita_menu_top(persona):
    if persona.volontario and not persona.ha_aspirante:
        if persona.ha_permesso(GESTIONE_SO_SEDE):
            return True
        elif persona.ha_permesso(GESTIONE_SERVIZI):
            return True
        else:
            # todo:
            return True
    return False


class CalendarTurniSO(HTMLCalendar):
    def __init__(self, date, turni):
        self.year = date.year
        self.month = date.month
        self.turni = turni
        super().__init__()

    def formatday(self, day):
        a = ''

        if day == 0:
            return '<td></td>'

        # 1: Trova turni con l'inizio questo gg, questo mese
        turni_per_giorno = self.turni.filter(Q(inizio__day=day),
                                             inizio__month=self.month)

        # 2: Memorizza i suoi numeri
        pk_tmp = list(turni_per_giorno.values_list('pk', flat=True))

        # 3: Ulteriore ricerca dei turni che hanno inizio prima o dopo questo mese
        for turno in self.turni:
            d = datetime(self.year, self.month, day)
            if turno.inizio <= d <= turno.fine:
                # 4. Memorizza anche questi turni
                pk_tmp.append(turno.pk)

        # 5. Query tutti turni insieme
        turni_per_giorno = self.turni.filter(pk__in=pk_tmp)

        # 6. Render dei link
        for turno in turni_per_giorno:
            a += "<a href='%s'>%s</a>" % (turno.url, turno.nome)

        return """<td>
        <span class='date'>%s</span> 
            <div class='so-calendar__day-items'>
                %s
            </div>
        </td>""" % (day, a)

    def formatweek(self, theweek):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d)
        return "<tr>%s</tr>" % week

    def formatmonth(self, withyear=True):
        html = ''
        html += self._replace_month_name(self.month, self.year)
        html += self._replace_day_name(self.formatweekheader())

        for week in self.monthdays2calendar(self.year, self.month):
            html += self.formatweek(week)

        return html

    def _replace_month_name(self, month, year):
        months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']
        months_it = ['', 'Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio',
            'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']

        en = months.pop(month)
        it = months_it.pop(month)

        html = '<tr><th colspan="7" class="month">%s</th></tr>' % en
        return html.replace(en, "%s %s" % (it, year))

    def _replace_day_name(self, html):
        new_html = html
        th = '">%s</th>'
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        days_it = ('Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica')

        for day in list(zip(days, days_it)):
            en = th % day[0]
            it = th % day[1]
            if en in new_html:
                new_html = new_html.replace(en, it)
        return new_html

    @staticmethod
    def prev_month(date):
        first = date.replace(day=1)
        prev_month = first - timedelta(days=1)
        return 'm=%s-%s' % (prev_month.year, prev_month.month)

    @staticmethod
    def next_month(date):
        days_in_month = monthrange(date.year, date.month)[1]
        last = date.replace(day=days_in_month)
        next_month = last + timedelta(days=1)
        return 'm=%s-%s' % (next_month.year, next_month.month)
