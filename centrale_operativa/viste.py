from datetime import timedelta, date

from django.db.models import Q, F
from django.shortcuts import redirect, get_object_or_404

from anagrafica.models import Appartenenza
from anagrafica.permessi.costanti import ERRORE_PERMESSI, GESTIONE_CENTRALE_OPERATIVA_SEDE, \
    GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE
from attivita.models import Partecipazione, Attivita
from autenticazione.funzioni import pagina_privata
from base.errori import errore_generico
from base.utils import poco_fa
from centrale_operativa.forms import ModuloNuovaReperibilita
from centrale_operativa.models import Reperibilita, Turno
from django.utils import timezone


@pagina_privata
def attivita_reperibilita(request, me):

    reperibilita = me.reperibilita.all()[:50]

    modulo = ModuloNuovaReperibilita(request.POST or None, initial={
        "inizio": poco_fa() + timedelta(hours=1),
        "fine": poco_fa() + timedelta(hours=2),
    })

    if modulo.is_valid():
        r = modulo.save(commit=False)
        r.persona = me
        r.save()
        return redirect("/attivita/reperibilita/")

    contesto = {
        "reperibilita": reperibilita,
        "modulo": modulo,
    }
    return "attivita_reperibilita.html", contesto


@pagina_privata
def attivita_reperibilita_cancella(request, me, reperibilita_pk=None):
    reperibilita = get_object_or_404(Reperibilita, pk=reperibilita_pk)
    if not reperibilita.persona == me:
        return redirect(ERRORE_PERMESSI)
    reperibilita.delete()
    return redirect("/attivita/reperibilita/")


@pagina_privata
def co(request, me):
    sedi = me.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE)
    contesto = {
        "sedi": sedi,
    }
    return "centrale_operativa.html", contesto


@pagina_privata
def co_reperibilita(request, me):
    sedi = me.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE)
    ora = poco_fa()
    reperibilita = Reperibilita.query_attuale(Appartenenza.query_attuale(sede__in=sedi).via("persona__appartenenze"),
                                              al_giorno=ora).order_by('attivazione', '-creazione')
    contesto = {
        "reperibilita": reperibilita,
        "ora": ora,
    }
    return "centrale_operativa_reperibilita.html", contesto


@pagina_privata
def co_poteri(request, me):
    sedi = me.oggetti_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE)

    minuti = Attivita.MINUTI_CENTRALE_OPERATIVA

    # Limiti di tempo per la centrale operativa
    quindici_minuti_fa = timezone.now() - timedelta(minutes=minuti)
    tra_quindici_minuti = timezone.now() + timedelta(minutes=minuti)

    partecipazioni = Partecipazione.con_esito_ok().filter(
        turno__inizio__lte=tra_quindici_minuti,
        turno__fine__gte=quindici_minuti_fa,
        turno__attivita__centrale_operativa=Attivita.CO_MANUALE,
        turno__attivita__sede__in=sedi,
    )

    contesto = {
        "partecipazioni": partecipazioni,
        "minuti": minuti,
    }
    return "centrale_operativa_poteri.html", contesto


@pagina_privata
def co_poteri_switch(request, me, part_pk):
    sedi = me.oggetti_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE)

    partecipazione = Partecipazione.con_esito_ok(
        turno__attivita__sede__in=sedi,
        pk=part_pk
    ).first()

    if not partecipazione:
        return errore_generico(request, me, titolo="Partecipazione non trovata")

    partecipazione.centrale_operativa = not partecipazione.centrale_operativa
    partecipazione.save()

    return redirect("/centrale-operativa/poteri/")


@pagina_privata
def co_turni(request, me):
    sedi = me.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE)
    tra_qualche_ora = poco_fa() + timedelta(hours=2)
    qualche_ora_fa = poco_fa() - timedelta(hours=2)
    partecipazioni = Partecipazione.con_esito_ok().filter(
            Q(turno__attivita__sede__in=sedi),                                       # Nelle mie sedi di competenza
            Q(turno__inizio__lte=tra_qualche_ora, turno__fine__gte=qualche_ora_fa)   # a) In corso, oppure
            | Q(turno__coturni__montato_da__isnull=False,
                turno__coturni__smontato_da__isnull=True)                            # d) Da smontare
        ).select_related('turno', 'turno__attivita', 'turno__attivita__sede')\
         .order_by('turno__inizio', 'turno__fine', 'turno__id', 'persona__id')\
         .distinct('turno__inizio', 'turno__fine', 'turno__id', 'persona__id')
    contesto = {
        "partecipazioni": partecipazioni,
    }
    return "centrale_operativa_turni.html", contesto


@pagina_privata
def co_turni_monta(request, me, partecipazione_pk=None):
    p = get_object_or_404(Partecipazione, pk=partecipazione_pk)
    if p.turno.attivita.sede not in me.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE):
        return redirect(ERRORE_PERMESSI)
    coturno = p.coturno()
    if coturno is not None:
        return redirect("/centrale-operativa/turni/")

    coturno = Turno(turno=p.turno, persona=p.persona, montato_da=me, montato_data=poco_fa())
    coturno.save()
    return redirect("/centrale-operativa/turni/")


@pagina_privata
def co_turni_smonta(request, me, partecipazione_pk=None):
    p = get_object_or_404(Partecipazione, pk=partecipazione_pk)
    if p.turno.attivita.sede not in me.oggetti_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE):
        return redirect(ERRORE_PERMESSI)
    coturno = p.coturno()
    if coturno is None:
        return redirect("/centrale-operativa/turni/")

    if not coturno.smontabile:
        return errore_generico(request, me, titolo="Questa persona non può essere smontata",
                               messaggio="Per qualche motivo la persona non è smontabile. Forse è già "
                                         "stata smontata da qualcun altro?", torna_titolo="Torna indietro",
                               torna_url="/centrale-operativa/turni/")

    coturno.smontato_data = poco_fa()
    coturno.smontato_da = me
    coturno.save()
    return redirect("/centrale-operativa/turni/")
