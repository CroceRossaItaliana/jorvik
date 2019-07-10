class MenuUtente:
    def __init__(self, me):
        self.me = me

    def __call__(self, *args, **kwargs):
        if self.me and not hasattr(self.me, 'aspirante'):
            return self.get_menu()
        else:
            return None

    @property
    def is_volontario(self):
        return self.me and self.me.volontario

    @property
    def is_donatore(self):
        return hasattr(self.me, 'donatore')

    def menu_volontario(self):
        return ("Volontario", (
            ("Estensione", "fa-random", "/utente/estensione/"),
            ("Trasferimento", "fa-arrow-right", "/utente/trasferimento/"),
            ("Riserva", "fa-pause", "/utente/riserva/"),
        ))

    def menu_persona(self):
        me = self.me
        return ("Persona", (
            ("Benvenuto", "fa-bolt", "/utente/"),
            ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
            ("Storico", "fa-clock-o", "/utente/storico/"),
            ("Documenti", "fa-folder", "/utente/documenti/") if me and (me.volontario or me.dipendente) else None,
            ("Contatti", "fa-envelope", "/utente/contatti/"),
            ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
        ))

    def menu_curriculum(self):
        me = self.me
        return ("Curriculum", (
            ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
            ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
            ("Patenti CRI", "fa-ambulance", "/utente/curriculum/PC/") if me and (me.volontario or me.dipendente) else None,
            ("Titoli CRI", "fa-plus-square-o", "/utente/curriculum/TC/") if me and (me.volontario or me.dipendente) else None,

            # Competenze personali commentate per non visuallizarle
            # ("Competenze personali", "fa-suitcase", "/utente/curriculum/CP/"),
        ))

    def menu_donatore(self):
        return ("Donatore", (
            ("Profilo Donatore", "fa-user", "/utente/donazioni/profilo/"),
            ("Donazioni di Sangue", "fa-flask", "/utente/donazioni/sangue/") if self.is_donatore else None,
        ))

    def menu_sicurezza(self):
        return ("Sicurezza", (
            ("Cambia password", "fa-key", "/utente/cambia-password/"),
            ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
        ))

    def menu_links(self):
        from ..models import Menu

        return ("Links", tuple((link.name, link.icon_class, link.url)
            for link in Menu.objects.filter(is_active=True).order_by('order')))

    def get_menu(self):
        from .utente_monitoraggio import menu_monitoraggio
        from .utente_rubrica import menu_rubrica_base

        return ((
            self.menu_persona(),
            self.menu_volontario() if self.is_volontario else None,
            menu_rubrica_base(self.me),
            self.menu_curriculum(),
            self.menu_donatore() if self.is_volontario else None,
            self.menu_sicurezza(),
            self.menu_links(),
            # menu_monitoraggio(self.me),
        ))
