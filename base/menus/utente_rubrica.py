def menu_rubrica_base(me):
    from django.core.urlresolvers import reverse
    from django.contrib.contenttypes.models import ContentType
    from anagrafica.permessi.applicazioni import (PRESIDENTE, COMMISSARIO, UFFICIO_SOCI, RUBRICHE_TITOLI, CONSIGLIERE_GIOVANE, CONSIGLIERE_GIOVANE_COOPTATO)
    from anagrafica.models import Sede


    RUBRICA_BASE = [
        ("Referenti", "fa-book", reverse('utente:rubrica', args=['referenti'])),
        ("Volontari", "fa-book", reverse('utente:rubrica', args=['volontari'])),
        ("Giovani", "fa-book", reverse('utente:rubrica', args=['giovani'])) if me.deleghe_attuali(
            tipo__in=[CONSIGLIERE_GIOVANE, CONSIGLIERE_GIOVANE_COOPTATO]
        ) else None,
    ]

    deleghe_attuali = None

    if me:
        tutte_deleghe_attuali = me.deleghe_attuali()

        deleghe_normali = tutte_deleghe_attuali.exclude(tipo=PRESIDENTE)
        sedi_deleghe_normali = me.sedi_deleghe_attuali(deleghe=deleghe_normali) if me else Sede.objects.none()
        sedi_deleghe_normali = [sede.pk for sede in sedi_deleghe_normali if sede.comitati_sottostanti().exists() or sede.unita_sottostanti().exists()]
        presidente = tutte_deleghe_attuali.filter(tipo=PRESIDENTE)
        sedi_deleghe_presidente = me.sedi_deleghe_attuali(deleghe=presidente) if me else Sede.objects.none()
        # sedi_presidenti_sottostanti = [sede.pk for sede in sedi_deleghe_presidente if sede.comitati_sottostanti().exists()]
        sedi_deleghe_presidente = list(sedi_deleghe_presidente.values_list('pk', flat=True))
        sedi = sedi_deleghe_normali + sedi_deleghe_presidente

        deleghe_attuali = me.deleghe_attuali(
            oggetto_tipo=ContentType.objects.get_for_model(Sede),
            oggetto_id__in=sedi
        ).distinct().values_list('tipo', flat=True)

    if deleghe_attuali:
        rubriche = list()

        for slug, informazioni in RUBRICHE_TITOLI.items():
            delega, titolo, espandi = informazioni
            if titolo not in rubriche:
                rubriche.append(titolo)

                if (delega in deleghe_attuali or
                        UFFICIO_SOCI in deleghe_attuali or
                        PRESIDENTE in deleghe_attuali or
                        COMMISSARIO in deleghe_attuali):

                    if UFFICIO_SOCI in deleghe_attuali and (delega == COMMISSARIO or delega == PRESIDENTE):
                        continue

                    url_item_to_rubrica = (titolo, "fa-book", reverse('utente:rubrica', args=[slug]))
                    RUBRICA_BASE.append(url_item_to_rubrica)

    # if UFFICIO_SOCI in deleghe_attuali:
    #     for rubrica in RUBRICA_BASE:
    #         if rubrica[0] == 'Commissari' or rubrica[0] == 'Presidenti':
    #             RUBRICA_BASE.remove(rubrica)

    VOCE_RUBRICA = ("Rubrica", (
        RUBRICA_BASE
    ))

    return VOCE_RUBRICA
