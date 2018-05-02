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
from gruppi.forms import ModuloGruppoSpecifico, ModuloGruppoNonSpecifico
from attivita.models import Attivita, Area, Partecipazione, Turno
from anagrafica.permessi.applicazioni import DELEGATO_AREA
from anagrafica.permessi.costanti import GESTIONE_ATTIVITA_AREA


@pagina_privata(permessi=GESTIONE_ATTIVITA_AREA)
def attivita_gruppo(request, me):
    """
    Crea gruppi di lavoro per il mio comitato o elimina quelli di cui sono responsabile.
    """
    # Sono responsabile di queste aree di intervento.
    area_permessi = me.oggetti_permesso(GESTIONE_ATTIVITA_AREA)
    id_sede_aree = area_permessi.values_list('sede_id', flat=True)

    # Attività nelle aree di cui sono responsabile.
    attivita_specifica = Attivita.objects.filter(area__in=area_permessi)

    # Gruppi nelle aree di cui sono responsabile.
    gruppi_gestione = Gruppo.objects.filter(area__in=area_permessi)

    modulo_attivita_specifica = ModuloGruppoSpecifico(request.POST or None, attivita_specifica=attivita_specifica,
                                                      request=request.POST)
    modulo_attivita_non_specifica = ModuloGruppoNonSpecifico(request.POST or None, area_permessi=area_permessi,
                                                             request=request.POST)

    if 'specifico' in request.POST:
        if modulo_attivita_specifica.is_valid():
            attivita_specifica = modulo_attivita_specifica.cleaned_data['attivita_specifica']
            area = Area.objects.get(id=attivita_specifica.area_id)
            Gruppo.objects.create(nome=attivita_specifica.nome, sede=attivita_specifica.sede,
                                  obiettivo=area.obiettivo, attivita=attivita_specifica,
                                  estensione=attivita_specifica.estensione.estensione,
                                  area=attivita_specifica.area)
            return messaggio_generico(request, None,
                                      titolo="Gruppo creato",
                                      messaggio="Hai creato un gruppo per un attività specifica",
                                      torna_url="/attivita/gruppo/",
                                      torna_titolo="Torna alla gestione dei gruppi")

    if 'non_specifico' in request.POST:
        if modulo_attivita_non_specifica.is_valid():
            nome_gruppo = modulo_attivita_non_specifica.cleaned_data['nome']
            area = modulo_attivita_non_specifica.cleaned_data['area']
            Gruppo.objects.create(nome=nome_gruppo, sede=area.sede, obiettivo=area.obiettivo,
                                  attivita=None, estensione=area.sede.estensione, area_id=area.id)
            return messaggio_generico(request, None,
                                      titolo="Gruppo creato",
                                      messaggio="Hai creato un gruppo per un'area",
                                      torna_url="/attivita/gruppo/",
                                      torna_titolo="Torna alla gestione dei gruppi")

    contesto = {
        "gruppi_gestione": gruppi_gestione,
        "modulo_attivita_specifica": modulo_attivita_specifica,
        "modulo_attivita_non_specifica": modulo_attivita_non_specifica,
    }
    return 'attivita_gruppo.html', contesto


@pagina_privata
def attivita_gruppi(request, me):
    """
    Mostra i gruppi di cui faccio parte, assieme ai controlli necessari a iscriversi a nuovi gruppi.
    """
    # Gruppi disponibili per attività non specifiche.
    gruppi_disponibili = Gruppo.objects.filter(sede__in=me.sedi_attuali().espandi(), attivita_id__isnull=True)

    # Attività a cui partecipo.
    partecipazioni_attivita_specifice = Partecipazione.objects.filter(persona=me, confermata=True
                                                                     ).values_list('turno', flat=True)
    attivita_specifiche = Turno.objects.filter(id=partecipazioni_attivita_specifice
                                              ).values_list('attivita', flat=True)

    # Gruppi disponibili per le attività a cui partecipo.
    gruppi_specifici_disponibili = Gruppo.objects.filter(attivita=attivita_specifiche)

    miei_gruppi = Gruppo.objects.filter(Appartenenza.query_attuale().via("appartenenze"),
                                        appartenenze__persona=me)
    gruppi_gestione = me.oggetti_permesso(GESTIONE_GRUPPO)

    contesto = {
        "gruppi_disponibili": gruppi_disponibili,
        "miei_gruppi": miei_gruppi,
        "gruppi_gestione": gruppi_gestione,
        "gruppi_specifici_disponibili": gruppi_specifici_disponibili
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
def attivita_gruppi_gruppo_elimina(request, me, pk):
    """
    Elimina un gruppo.
    """
    # Verifica se sono un delegato d'area.
    if not me.deleghe_attuali(tipo=DELEGATO_AREA).exists():
        return redirect(ERRORE_PERMESSI)

    gruppo = get_object_or_404(Gruppo, pk=pk)
    gruppo.delete()

    return messaggio_generico(request, me, titolo="Hai eliminato il gruppo",
                              messaggio="Il gruppo '%s' è stato eliminato con successo." % (
                                  gruppo.nome,
                              ), torna_titolo="Torna a crea gruppo",
                              torna_url="/attivita/gruppo/")


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
