from django.core.urlresolvers import reverse
from anagrafica.models import Appartenenza
from .utente_monitoraggio import menu_monitoraggio
from ..models import Menu, MenuSegmento
from jorvik import settings


class MenuUtente:
    def __init__(self, me):
        self.me = me

    def __call__(self, *args, **kwargs):
        if self.me and not hasattr(self.me, 'aspirante'):
            return self.get_menu()
        elif self.me.appartenenze_attuali(membro=Appartenenza.SEVIZIO_CIVILE_UNIVERSALE).exists():
            return self.get_menu()
        else:
            return None

    @staticmethod
    def _espandi_con_static_pege(menu, persona):
        menu_segmenti = MenuSegmento.objects.distinct().all().filtra_per_segmenti(utente=persona)
        return tuple((link.name, link.icon_class, link.url)
              for link in Menu.objects.distinct().filter(is_active=True, menu=menu, segmenti__in=menu_segmenti).order_by('order'))



    @property
    def is_volontario(self):
        return self.me and self.me.volontario

    @property
    def is_donatore(self):
        return hasattr(self.me, 'donatore')

    def menu_volontario(self):
        return ("Volontario", (
            ("Estensione", "fa-random", reverse('utente:estensione')),
            ("Trasferimento", "fa-arrow-right", reverse('utente:trasferimento')),
            ("Riserva", "fa-pause", reverse('utente:riserva')),
        ) + self._espandi_con_static_pege(Menu.VOLONTARIO, self.me))

    def menu_formazione(self):
        from formazione.menus import formazione_menu

        menu = list(formazione_menu('formazione', self.me)[0])

        menu[0] = "Formazione"
        questionario_fabbisogni_formativi_territoriali = (("Fabbisogni Formativi Comitato Territoriale", 'fa-user', reverse('pages:monitoraggio-fabb-info-territoriale')) if (
                        self.me.is_presidente_o_commissario_territoriale or self.me.is_responsabile_formazione_territoriale) else None, )
        questionario_fabbisogni_formativi_regionali = (
            ("Fabbisogni Formativi Comitato Regionale", 'fa-user', reverse('pages:monitoraggio-fabb-info-regionale')) if (
                    self.me.is_presidente_o_commissario_regionale or self.me.is_responsabile_formazione_regionale) else None,)
        monitora_fabbisogni_formativi_territoriali = ("Monitora Fabbisogni Formativi Territoriali", 'fa-user', reverse('pages:monitora-fabb-info-territoriale')) if (
                self.me.delega_presidente_e_commissario_regionale or self.me.is_delgato_regionale_monitoraggio_fabbisogni_informativi
        ) else None,
        monitora_fabbisogni_formativi_regionali = ("Monitora Fabbisogni Formativi", 'fa-user',
                                                   reverse('pages:monitora-fabb-info-regionale')) if (
                self.me.is_responsabile_formazione_nazionale
        ) else None,
        # menu[1] = questionario_fabbisogni_formativi_regionali + \
        #           questionario_fabbisogni_formativi_territoriali + \
        #           monitora_fabbisogni_formativi_territoriali + \
        #           monitora_fabbisogni_formativi_regionali + \
        #           menu[1]
        menu[1] += self._espandi_con_static_pege(Menu.FORMAZIONE, self.me)
        return menu

    def menu_persona(self):
        me = self.me
        return ("Persona", (
            ("Benvenuto", "fa-bolt", "/utente/"),
            ("Anagrafica", "fa-edit", "/utente/anagrafica/"),
            ("Storico", "fa-clock", "/utente/storico/"),
            ("Documenti", "fa-folder", "/utente/documenti/") if me and (
                    me.volontario or me.dipendente or me.servizio_civile
            ) else None,
            ("Contatti", "fa-envelope", "/utente/contatti/"),
            ("Fotografie", "fa-credit-card", "/utente/fotografia/"),
            ("Le mie visite mediche", "fa-notes-medical",
             "/utente/visite-mediche/") if settings.VISITE_ENABLED and (
                me and me.volontario
            ) else None,
        ) + self._espandi_con_static_pege(Menu.PERSONA, self.me))

    def menu_curriculum(self):
        me = self.me
        return ("Curriculum", (
            ("Patenti Civili", "fa-car", "/utente/curriculum/PP/"),
            ("Titoli di Studio", "fa-graduation-cap", "/utente/curriculum/TS/"),
            ("Patenti CRI", "fa-ambulance", "/utente/curriculum/PC/") if me and (me.volontario or me.dipendente) else None,
            ("Qualifiche CRI", "fa-plus-square", "/utente/curriculum/TC/") if me and (me.volontario or me.dipendente) else None,
            ("Altre Qualifiche", "fa-plus-square", "/utente/curriculum/AT/") if me and (me.volontario or me.dipendente) else None,
            ("Conoscenza Linguistiche", "fa-graduation-cap", "/utente/curriculum/CL/") if me and (me.volontario or me.dipendente) else None,
            ("Professionalità e Competenze/Skills", "fa-plus-square", "/utente/curriculum/CS/") if me and (me.volontario or me.dipendente) else None,
        ) + self._espandi_con_static_pege(Menu.CURRICULUM, self.me))

    def menu_donatore(self):
        return ("Donatore", (
            ("Profilo Donatore", "fa-user", "/utente/donazioni/profilo/"),
            ("Donazioni di Sangue", "fa-flask", "/utente/donazioni/sangue/") if self.is_donatore else None,
        ) + self._espandi_con_static_pege(Menu.DONATORE, self.me))

    def menu_sicurezza(self):
        return ("Sicurezza", (
            ("Cambia password", "fa-key", "/utente/cambia-password/"),
            ("Impostazioni Privacy", "fa-cogs", "/utente/privacy/"),
        ) + self._espandi_con_static_pege(Menu.SICUREZZA, self.me))

    def menu_links(self):
        return ("Links", self._espandi_con_static_pege(Menu.LINK, self.me))

    def menu_novita(self):
        return ("Novità", self._espandi_con_static_pege(Menu.NOVITA, self.me))

    def get_menu(self):
        from .utente_rubrica import menu_rubrica_base

        me = self.me

        if me.operatore_villa_maraini and not me.volontario:
            return ((
                self.menu_persona(),
                self.menu_sicurezza(),
            ))
        else:
            return ((
                self.menu_persona(),
                self.menu_volontario() if me.volontario else None,
                self.menu_formazione() if me.volontario or me.dipendente or me.servizio_civile else None,
                menu_rubrica_base(me),
                self.menu_curriculum(),
                self.menu_donatore() if self.is_volontario else None,
                self.menu_sicurezza(),
                self.menu_links(),
                self.menu_novita(),
                menu_monitoraggio(me),
            ))
