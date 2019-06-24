class Menu:
    def __init__(self, request):
        self.me = request.me if hasattr(request, 'me') else None
        self.request = request
        # self.section = request.POST['section']

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

        return utente.MenuUtente(self.me)()

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
        from .menus import autorizzazioni

        return autorizzazioni.menu_autorizzazioni(self.request, self.me)

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

    def get_menu(self):
        from .utils import remove_none

        # Map request to class-methods
        mapping = {
            'utente': self.elementi_anagrafica,
            'centrale-operativa': self.centrale_operativa,
        }

        section_name = ''.join(self.request.path.split('/'))

        if not hasattr(self, section_name):
            get_elements_for_section = mapping[section_name]
        else:
            get_elements_for_section = getattr(self, section_name)

        return {section_name: remove_none(get_elements_for_section)}





# def menu(request):
#     me = request.me if hasattr(request, 'me') else None
#     section = request.POST['section']
#     gestione_corsi_sede = me.ha_permesso(GESTIONE_CORSI_SEDE) if me else False

    # elementi = {    #
    #     "utente": utente.MenuUtente(me)(),
    #     "posta": posta.menu_posta(me),
    #     "veicoli": veicoli.menu_veicoli(me),
    #     "attivita": attivita.menu_attivita(me) if me and me.volontario else None,
    #     "autorizzazioni": autorizzazioni.menu_autorizzazioni(request, me),
    #     "presidente": presidente.menu_presidente(me),
    #     "us": ufficio_soci.menu_us(me),
    #     "co": centrale_operativa.menu_co(me),
    #
    #     "formazione": (
    #         ("Corsi Base", (
    #             ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
    #             ("Domanda formativa", "fa-area-chart", "/formazione/corsi-base/domanda/")
    #                 if gestione_corsi_sede else None,
    #             ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-base/nuovo/")
    #                 if gestione_corsi_sede else None,
    #             # ("Monitoraggio 2019", 'fa-user', reverse('pages:monitoraggio'))
    #             #     if me and (me.is_presidente or me.is_comissario) else None,
    #         )),
    #         ("Corsi di Formazione", (
    #             ("Elenco Corsi di Formazione", "fa-list", "/formazione/corsi-formazione/"),
    #             ("Pianifica nuovo", "fa-asterisk", "/formazione/corsi-formazione/nuovo/"),
    #         )) if False else None,
    #     ),
    #     "aspirante": (
    #         ("Aspirante", (
    #             ("Home page", "fa-home", "/aspirante/"),
    #             ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
    #             ("Storico", "fa-clock-o", "/utente/storico/"),
    #             ("Contatti", "fa-envelope", "/utente/contatti/"),
    #             ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
    #             ("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
    #             ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
    #             ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
    #         )),
    #         ("Nelle vicinanze", (
    #             ("Impostazioni", "fa-gears", "/aspirante/impostazioni/"),
    #             ("Corsi Base", "fa-list", "/aspirante/corsi-base/"),
    #             ("Sedi CRI", "fa-list", "/aspirante/sedi/"),
    #         )),
    #         ("Sicurezza", (
    #             ("Cambia password", "fa-key", "/utente/cambia-password/"),
    #             ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
    #         ),
    #         ),
    #     ) if me and hasattr(me, 'aspirante') else (
    #         ("Gestione Corsi", (
    #             ("Elenco Corsi Base", "fa-list", "/formazione/corsi-base/elenco/"),
    #         )),
    #     ),
    # }
    # if me and hasattr(me, 'aspirante'):
    #     elementi['elementi_anagrafica'] = elementi.get('aspirante')
    # else:
    #     elementi['elementi_anagrafica'] = elementi.get('utente')
    #
    # elementi = elementi.get(section)

    # return remove_none(elementi)
