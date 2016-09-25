from datetime import timedelta, date, datetime, time
from django.db.models import Count, F, Sum
from attivita.models import Attivita, Turno, Partecipazione
import json

from base.utils import timedelta_ore


def statistiche_attivita_persona(persona, modulo):
    """
    Ritorna un dizionario di parametri, che puo' essere passato alla vista,
    con tutti i dati statistici relativi alle attivita' effettuate da una determinata
    persona.

    :param persona_id: ID della persona.
    :param modulo: Il form validato.
    :return: Un dizionario, o None se il form non e' valido.
    """

    if not modulo.is_valid():
        return None

    oggi = date.today()

    impostazioni = {
        # num_giorni: (nome, numero_periodi)
        modulo.SETTIMANA: ("sett.", 20),
        modulo.QUINDICI_GIORNI: ("fortn.", 20),
        modulo.MESE: ("mesi", 12),
        modulo.ANNO: ("anni", 4),
    }

    giorni = int(modulo.cleaned_data['periodo'])
    etichetta, periodi = impostazioni[giorni]

    statistiche = []
    chart = {}

    for periodo in range(periodi, -1, -1):

        dati = {}

        fine = oggi - timedelta(days=(giorni * periodo))
        inizio = fine - timedelta(days=giorni - 1)

        fine = datetime.combine(fine, time(23, 59, 59))
        inizio = datetime.combine(inizio, time(0, 0, 0))

        dati['inizio'] = inizio
        dati['fine'] = fine

        # Prima, ottiene tutti i queryset.
        qs_turni = Turno.objects.filter(inizio__lte=fine, fine__gte=inizio)
        qs_part = Partecipazione.con_esito_ok(turno__in=qs_turni, persona=persona)

        ore_di_servizio = qs_part.annotate(durata=F('turno__fine') - F('turno__inizio'))\
            .aggregate(totale_ore=Sum('durata'))['totale_ore'] or timedelta()

        # Poi, associa al dizionario statistiche.
        dati['etichetta'] = "%d %s fa" % (periodo, etichetta,)
        dati['num_turni'] = qs_part.count()
        dati['ore_di_servizio'] = ore_di_servizio
        dati['ore_di_servizio_int'] = round(ore_di_servizio.total_seconds() / 3600, 3)

        statistiche.append(dati)

    chart['labels'] = json.dumps([x['etichetta'] for x in statistiche])
    chart['num_turni'] = json.dumps([x['num_turni'] for x in statistiche])
    chart['ore_di_servizio'] = json.dumps([timedelta_ore(x['ore_di_servizio']) for x in statistiche])

    return {'statistiche': statistiche,
            'chart': chart}

