def menu_co(me):
    from anagrafica.permessi.costanti import GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE

    return (
        ("Centrale Operativa", (
            ("Reperibilità", "fa-clock-o", "/centrale-operativa/reperibilita/"),
            ("Turni", "fa-calendar", "/centrale-operativa/turni/"),
            ("Poteri", "fa-magic", "/centrale-operativa/poteri/")
            if me and me.oggetti_permesso(GESTIONE_POTERI_CENTRALE_OPERATIVA_SEDE).exists() else None,
        )),
    )
