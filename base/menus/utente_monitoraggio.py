def menu_monitoraggio(me):
    from django.core.urlresolvers import reverse
    from anagrafica.permessi.applicazioni import PRESIDENTE, COMMISSARIO
    from static_page.monitoraggio import TypeFormNonSonoUnBersaglio

    deleghe_monitoraggio = me.deleghe_attuali(tipo__in=[PRESIDENTE, COMMISSARIO]) if me else None

    link_bersaglio = None
    last_delega = deleghe_monitoraggio.last()
    if last_delega:
        last_delega_id = last_delega.oggetto_id
        first_typeform = TypeFormNonSonoUnBersaglio(None, me).get_first_typeform()

        link_bersaglio = reverse('pages:monitoraggio-nonsonounbersaglio')
        if len(deleghe_monitoraggio) == 1:
            link_bersaglio += '?comitato=%s&id=%s' % (last_delega_id, first_typeform)

    delega_regionale = me.delega_presdente_regionale
    id_regionale = None
    if delega_regionale:
        id_regionale = delega_regionale.oggetto.id

    VOCE_MONITORAGGIO = ("Check-list Comitati", (
        ("Questionario di autocontrollo", 'fa-user', reverse('pages:monitoraggio')) if (
                me.is_presidente or me.is_comissario
        ) else None,
        ("Questionario L. 124/2017", 'fa-user', reverse('pages:monitoraggio-trasparenza')) if (
                me.is_presidente or me.is_comissario or me.delega_responsabile_area_trasparenza
        ) else None,
        ("Monitora Trasparenza L. 124/2017", 'fa-user', reverse('pages:monitora-trasparenza')+'?r={}'.format(id_regionale)) if
                delega_regionale else None,
        ("Monitora Trasparenza L. 124/2017", 'fa-user', reverse('pages:monitora-trasparenza')) if
                me.is_responsabile_area_monitoraggio_trasparenza else None,
        # ("Monitoraggio NON SONO UN BERSAGLIO", 'fa-user', link_bersaglio) if link_bersaglio else None,
    ))

    return VOCE_MONITORAGGIO if me and (
            me.is_presidente or me.is_comissario or me.is_responsabile_area_monitoraggio_trasparenza or me.delega_responsabile_area_trasparenza
    ) else None
