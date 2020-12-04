from django.core.urlresolvers import reverse
from formazione.menus import formazione_menu
from anagrafica.models import Appartenenza

class Menu:
    def __init__(self, request):
        self.me = request.me if hasattr(request, 'me') else None
        self.request = request

    @property
    def is_volontario(self):
        return self.me and self.me.volontario

    @property
    def is_aspirante(self):
        return self.me and hasattr(self.me, 'aspirante') and not self.me.appartenenze_attuali(membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE).exists()

    @property
    def is_sevizio_civile(self):
        return self.me.appartenenze_attuali(membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE).exists()

    @property
    def gestione_corsi_sede(self):
        from anagrafica.permessi.costanti import GESTIONE_CORSI_SEDE

        return self.me.ha_permesso(GESTIONE_CORSI_SEDE) if self.me else False

    @property
    def elementi_anagrafica(self):
        if self.is_aspirante:
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
    def so(self):
        from sala_operativa.menus import sala_operativa

        return sala_operativa(self.me)

    @property
    def co(self):
        from .menus import centrale_operativa

        return centrale_operativa.menu_co(self.me)

    @property
    def formazione(self):
        return formazione_menu('formazione', self.me)

    @property
    def aspirante(self):
        return formazione_menu('aspirante') if self.is_aspirante else self.formazione

    def mapping(self):
        """
        Il mapping serve a trovare il metodo che restituisce il menu laterale per ogni sezione.

        Con il mapping è facile restituire un menu (metodo) personalizzato per ogni request.path.

        urls - sono inizio del request.path che chiama utente per il quale si cerca un metodo
        method - metodo che restituisce il menu
        name_for_template - ogni template <***_vuoto.html> chiama una sua chiave del dizionario
        """

        return (
            ({
                'urls': ['/utente/', '/profilo/', '/page/', '/cv/'],
                'method': 'elementi_anagrafica',
                'name_for_template': 'elementi_anagrafica',
            }),
            ({
                'urls': ['/attivita/', '/informazioni/',],
                'method': 'attivita',
                'name_for_template': 'attivita',
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
                'urls': ['/us/'],
                'method': 'us',
                'name_for_template': 'us',
            }),
            ({
                'urls': ['/so/'],
                'method': 'so',
                'name_for_template': 'so',
            }),
            ({
                'urls': ['/veicoli/', '/veicolo/', '/autoparco/'],
                'method': 'veicoli',
                'name_for_template': 'veicoli',
            }),
            ({
                'urls': ['/centrale-operativa/'],
                'method': 'co',
                'name_for_template': 'co',
            }),
            ({
                'urls': ['/formazione/', '/courses/', '/survey/course/'],
                'method': 'formazione',
                'name_for_template': 'formazione',
            }),
            ({
                'urls': ['/aspirante/',],
                'method': 'aspirante',
                'name_for_template': 'aspirante',
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
        )

    def articoli(self):
        return (
            ("Articoli", (
                ("Elenco", "fa-newspaper-o", reverse('articoli:lista')),
            )),
        )

    def documenti(self):
        return (
            ("Documenti", (
                ("Elenco", "fa-newspaper-o", reverse('documenti:lista_documenti')),
                (
                    "Documenti comitato", "fa-newspaper-o", reverse('documenti:documenti-comitato')
                ) if self.me.is_presidente or self.me.is_comissario else None
            )),
        )

    def get_menu(self):
        from .utils import remove_none

        path = self.request.path

        # La ricerca del menu viene per inizio del url che chiama utente
        for i in self.mapping():
            for url in i['urls']:
                if path.startswith(url):
                    menu = remove_none(getattr(self, i['method']))
                    name_for_template = i['name_for_template']
                    return {name_for_template: menu}

        # Non restituisce nulla. Il menu sarè vuoto.
        return {None: []}
