
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from anagrafica.models import Sede, Persona
from anagrafica.models import Appartenenza as App
from anagrafica.permessi.costanti import GESTIONE_GRUPPO, MODIFICA, ERRORE_PERMESSI
from autenticazione.funzioni import pagina_privata
from base.errori import messaggio_generico
from base.utils import poco_fa
from gruppi.elenchi import ElencoMembriGruppo
from gruppi.models import Gruppo, Appartenenza


@pagina_privata
def attivita_gruppi(request, me):
    """
    Mostra i gruppi di cui faccio parte, assieme ai controlli necessari a iscriversi a nuovi gruppi.
    """
    gruppi_disponibili = Gruppo.objects.filter(sede__in=me.sedi_attuali().espandi())
    miei_gruppi = Gruppo.objects.filter(Appartenenza.query_attuale().via("appartenenze"), appartenenze__persona=me)
    gruppi_gestione = me.oggetti_permesso(GESTIONE_GRUPPO)

    contesto = {
        "gruppi_disponibili": gruppi_disponibili,
        "miei_gruppi": miei_gruppi,
        "gruppi_gestione": gruppi_gestione
    }
    return 'attivita_gruppi.html', contesto


@pagina_privata
def attivita_gruppi_gruppo(request, me, pk):
    """
    Mostra i membri del gruppo
    """
    gruppo = get_object_or_404(Gruppo, pk=pk)
    if not me.permessi_almeno(gruppo, MODIFICA):
        return redirect(ERRORE_PERMESSI)

    sedi = Sede.objects.filter(App.query_attuale().via("appartenenze"),
                               appartenenze__persona__appartenenze_gruppi__in=gruppo.appartenenze.all())
    elenco = ElencoMembriGruppo(sedi, gruppo, gruppo=gruppo)

    contesto = {
        "elenco": elenco,
        "gruppo": gruppo,
    }
    return 'attivita_gruppi_gruppo.html', contesto


@pagina_privata
def attivita_gruppi_gruppo_abbandona(request, me, pk):
    """
    Abbandona un gruppo.
    """
    gruppo = get_object_or_404(Gruppo, pk=pk)
    Appartenenza.query_attuale().filter(
        gruppo=gruppo, persona=me
    ).update(fine=poco_fa())
    return messaggio_generico(request, me, titolo="Hai abbandonato il gruppo",
                              messaggio="Non fai più parte del gruppo '%s'. <br />"
                                        "Sei stato disiscritto con successo." % (
                                  gruppo.nome,
                              ), torna_titolo="Torna all'elenco dei gruppi",
                              torna_url="/attivita/gruppi/")


@pagina_privata
def attivita_gruppi_gruppo_espelli(request, me, pk, persona_pk):
    """
    Abbandona un gruppo.
    """
    gruppo = get_object_or_404(Gruppo, pk=pk)
    if not me.permessi_almeno(gruppo, MODIFICA):
        return redirect(ERRORE_PERMESSI)
    persona = get_object_or_404(Persona, pk=persona_pk)
    Appartenenza.query_attuale().filter(
        gruppo=gruppo, persona=persona
    ).update(fine=poco_fa())
    return redirect("/attivita/gruppi/%d/?espulso=%d" % (
        gruppo.pk, persona.pk
    ))


@pagina_privata
def attivita_gruppi_gruppo_iscriviti(request, me, pk):
    """
    Abbandona un gruppo.
    """
    gruppo = get_object_or_404(Gruppo, pk=pk)
    if Appartenenza.query_attuale().filter(
        gruppo=gruppo, persona=me
    ).exists():  # Gia membro
        return redirect("/attivita/gruppi/?gia_membro")

    a = Appartenenza(
        gruppo=gruppo,
        persona=me,
        inizio=poco_fa()
    )
    a.save()

    return messaggio_generico(request, me, titolo="Iscrizione effettuata",
                              messaggio="Sei ora iscritt%s al gruppo di lavoro '%s'. <br />"
                                        "Riceverai per e-mail tutte le comunicazioni "
                                        "relative a questo gruppo" % (
                                  me.genere_o_a, gruppo.nome,
                              ), torna_titolo="Torna all'elenco dei gruppi",
                              torna_url="/attivita/gruppi/")
