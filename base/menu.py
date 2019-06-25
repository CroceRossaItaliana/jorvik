class Menu:
    def __init__(self, request):
        self.me = request.me if hasattr(request, 'me') else None
        self.request = request

    @property
    def is_volontario(self):
        return self.me and self.me.volontario

    @property
    def gestione_corsi_sede(self):
        from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE

        return self.me.ha_permesso(GESTIONE_CORSI_SEDE) if self.me else False

    @property
    def elementi_anagrafica(self):
        if self.me and hasattr(self.me, 'aspirante'):
            return self.aspirante
        else:
            return self.utente

    @property
    def utente(self):
        from .menus import utente

        menu_utente = utente.MenuUtente(self.me)
        return menu_utente()

    @property
    def attivita(self):
        from .menus import attivita

        return attivita.menu_attivita(self.me) if self.is_volontario else None

    @property
    def veicoli(self):
        return (
            ("Veicoli", (
                ("Dashboard", "fa-gears", "/veicoli/"),
                ("Veicoli", "fa-car", "/veicoli/elenco/"),
                ("Autoparchi", "fa-dashboard", "/veicoli/autoparchi/"),
            )),
        )

    @property
    def posta(self):
        return (
            ("Posta", (
                ("Scrivi", "fa-pencil", "/posta/scrivi/"),
                ("In arrivo", "fa-inbox", "/posta/in-arrivo/"),
                ("In uscita", "fa-mail-forward", "/posta/in-uscita/"),
            )),
        )

    @property
    def autorizzazioni(self):
        return (
            ("Richieste", (
                ("In attesa", "fa-user-plus", "/autorizzazioni/"),
                ("Storico", "fa-clock-o", "/autorizzazioni/storico/"),
            )),
            ("Ordina", (
                ("Dalla più recente", "fa-sort-numeric-desc", "?ordine=DESC",
                 self.request.GET.get('ordine', default="DESC") == "DESC"),
                ("Dalla più vecchia", "fa-sort-numeric-asc", "?ordine=ASC",
                 self.request.GET.get('ordine', default="DESC") == "ASC"),
            )),
        )

    @property
    def presidente(self):
        return (
            ("Sedi CRI", (
                ("Elenco", "fa-list", "/presidente/"),
            )),
        )

    @property
    def us(self):
        from .menus import ufficio_soci

        return ufficio_soci.menu_us(self.me)

    @property
    def co(self):
        from .menus import centrale_operativa

        return centrale_operativa.menu_co(self.me)

    @property
    def formazione(self):
        return (
            ("Corsi Base", (
                ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
                ("Domanda formativa", "fa-area-chart", "/formazione/corsi-base/domanda/")
                    if self.gestione_corsi_sede else None,
                ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-base/nuovo/")
                    if self.gestione_corsi_sede else None,
            )),
            ("Corsi di Formazione", (
                ("Elenco Corsi di Formazione", "fa-list", "/formazione/corsi-formazione/"),
                ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-formazione/nuovo/"),
            )) if False else None,
        )

    @property
    def aspirante(self):
        return (
            ("Aspirante", (
                ("Home page", "fa-home", "/aspirante/"),
                ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
                ("Storico", "fa-clock-o", "/utente/storico/"),
                ("Contatti", "fa-envelope", "/utente/contatti/"),
                ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
                ("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
                ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
                ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
            )),
            ("Nelle vicinanze", (
                ("Impostazioni", "fa-gears", "/aspirante/impostazioni/"),
                ("Corsi Base", "fa-list", "/aspirante/corsi-base/"),
                ("Sedi CRI", "fa-list", "/aspirante/sedi/"),
            )),
            ("Sicurezza", (
                ("Cambia password", "fa-key", "/utente/cambia-password/"),
                ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
            ),
            ),
        ) if self.me and hasattr(self.me, 'aspirante') else (
            ("Gestione Corsi", (
                ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
            )),
        )

    def mapping(self):
        return (
            ({
                'urls': ['/utente/', '/profilo/', '/page/'],
                'method': 'elementi_anagrafica',
                'name_for_template': 'elementi_anagrafica',
            }),
            ({
                'urls': ['/informazioni/', '/attivita/'],
                'method': 'attivita',
                'name_for_template': 'attivita',
            }),
            ({
                'urls': ['/centrale-operativa/'],
                'method': 'co',
                'name_for_template': 'co',
            }),
            ({
                'urls': ['/us/'],
                'method': 'us',
                'name_for_template': 'us',
            }),
            ({
                'urls': ['/posta/'],
                'method': 'posta',
                'name_for_template': 'posta',
            }),
            ({
                'urls': ['/autorizzazioni/'],
                'method': 'autorizzazioni',
                'name_for_template': 'autorizzazioni',
            }),
            ({
                'urls': ['/presidente/', '/strumenti/delegati/'],
                'method': 'presidente',
                'name_for_template': 'presidente',
            }),
            ({
                'urls': ['/articoli/'],
                'method': 'articoli',
                'name_for_template': 'articoli',
            }),
            ({
                'urls': ['/documenti/'],
                'method': 'documenti',
                'name_for_template': 'documenti',
            }),
            ({
                'urls': ['/veicoli/', '/veicolo/', '/autoparco/'],
                'method': 'veicoli',
                'name_for_template': 'veicoli',
            }),
            ({
                'urls': ['/formazione/', '/courses/'],
                'method': 'formazione',
                'name_for_template': 'formazione',
            }),
            ({
                'urls': ['/aspirante/',],
                'method': 'aspirante',
                'name_for_template': 'aspirante',
            }),
        )

    def get_menu(self):
        from .utils import remove_none

        path = self.request.path

        for i in self.mapping():
            for url in i['urls']:
                if path.startswith(url):
                    menu = remove_none(getattr(self, i['method']))
                    name_for_template = i['name_for_template']
                    return {name_for_template: menu}

        return {None: []}
