def menu_autorizzazioni(request, me):
    return (
        ("Richieste", (
            ("In attesa", "fa-user-plus", "/autorizzazioni/"),
            ("Storico", "fa-clock-o", "/autorizzazioni/storico/"),
        )),
        ("Ordina", (
            ("Dalla più recente", "fa-sort-numeric-desc", "?ordine=DESC",
             request.GET.get('ordine', default="DESC") == "DESC"),
            ("Dalla più vecchia", "fa-sort-numeric-asc", "?ordine=ASC",
             request.GET.get('ordine', default="DESC") == "ASC"),
        )),
    )
