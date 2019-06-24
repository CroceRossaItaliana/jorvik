def menu_monitoraggio(me):
    from django.core.urlresolvers import reverse
    from anagrafica.permessi.applicazioni import PRESIDENTE, COMMISSARIO
    from static_page.monitoraggio import TypeFormNonSonoUnBersaglio

    deleghe_monitoraggio = me.deleghe_attuali(tipo__in=[PRESIDENTE, COMMISSARIO]) if me else None

    last_delega_id = deleghe_monitoraggio.last().oggetto_id
    first_typeform = TypeFormNonSonoUnBersaglio(None, me).get_first_typeform()

    link_bersaglio = reverse('pages:monitoraggio-nonsonounbersaglio')
    if len(deleghe_monitoraggio) == 1:
        link_bersaglio += '?comitato=%s&id=%s' % (last_delega_id, first_typeform)

    VOCE_MONITORAGGIO = ("Monitoraggio", (
        ("Monitoraggio 2019 (dati 2018)", 'fa-user', reverse('pages:monitoraggio')),
        ("Monitoraggio NON SONO UN BERSAGLIO", 'fa-user', link_bersaglio),
    ))

    return VOCE_MONITORAGGIO if me and (me.is_presidente or me.is_comissario) else None
