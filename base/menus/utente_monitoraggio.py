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



    VOCE_MONITORAGGIO = ("Check-list Comitati", (
        ("Questionario di autocontrollo", 'fa-user', reverse('pages:monitoraggio')) if (
                me.is_presidente or me.is_comissario or me.delega_responsabile_area_trasparenza
        ) else None,
        ("Questionario L. 124/2017", 'fa-user', reverse('pages:monitoraggio-trasparenza')) if (
                me.is_presidente or me.is_comissario or me.delega_responsabile_area_trasparenza
        ) else None,
        # ("Monitora Trasparenza L. 124/2017", 'fa-user', reverse('pages:monitora-trasparenza')+'?r={}'.format(id_regionale)) if
        #         id_regionale else None,
        ("Monitora Autocontrollo", 'fa-user', reverse('pages:monitora-autocontrollo')) if (
                me.delega_presidente_e_commissario_regionale or me.is_responsabile_area_monitoraggio_trasparenza or me.is_delgato_regionale_monitoraggio_trasparenza
        ) else None,
        # ("Monitora Trasparenza L. 124/2017", 'fa-user', reverse('pages:monitora-trasparenza')) if
        ("Monitora Trasparenza L. 124/2017", 'fa-user', reverse('pages:monitoraggio-trasparenza')) if
        me.delega_presidente_e_commissario_regionale or me.is_responsabile_area_monitoraggio_trasparenza or me.is_delgato_regionale_monitoraggio_trasparenza or me.delegato_supervisore_monitoraggio else None,
        # ("Monitoraggio NON SONO UN BERSAGLIO", 'fa-user', link_bersaglio) if link_bersaglio else None,
    ))

    return VOCE_MONITORAGGIO if me and (
            me.is_presidente or me.is_comissario or me.is_responsabile_area_monitoraggio_trasparenza or me.delega_responsabile_area_trasparenza
    ) else None
