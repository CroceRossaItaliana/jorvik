from django.db.models import Q

from autocomplete_light import shortcuts as autocomplete_light

from .costanti import NAZIONALE, REGIONALE, PROVINCIALE, LOCALE, TERRITORIALE
from .permessi.applicazioni import UFFICIO_SOCI_UNITA, UFFICIO_SOCI
from .permessi.costanti import GESTIONE_CORSI_SEDE
from .models import Persona, Sede, Appartenenza
from formazione.models import PartecipazioneCorsoBase


class AutocompletamentoBase(autocomplete_light.AutocompleteModelBase):
    split_words = True

    @property
    def persona(self):
        return self.request.user.persona

    empty_html_format = "<span class=\"block allinea-centro text-muted\">" \
                        "<strong><i class=\"fa fa-fw fa-search\"></i> Nessun risultato.</strong><br />" \
                        "&nbsp;Prova a cambiare il termine di ricerca.&nbsp;" \
                        "<!--%s--></span>"

    attrs = {
        'placeholder': 'Inizia a scrivere...',
        'required': False,
    }


class PersonaAutocompletamento(AutocompletamentoBase):
    search_fields = ['nome', 'cognome', 'codice_fiscale', ]
    model = Persona
    choice_html_format = u'''
        <span class="block" data-value="%s"><strong>%s</strong> %s</span>
    '''

    def choices_for_request(self, filtra_per_sede=True):
        persona = self.request.user.persona

        # Le mie sedi di competenza:
        #  1. La mia Sede attuale
        #  2. Il mio Comitato
        #  3. Le mie Sedi di competenza
        sedi_attuali = persona.sedi_attuali()
        sedi_comitato = sedi_attuali.ottieni_comitati().espandi()
        sedi_competenza = persona.sedi_deleghe_attuali(espandi=True, pubblici=True)
        sedi = sedi_attuali | sedi_comitato | sedi_competenza

        # 1. Appartenente a una delle sedi
        q_appartenenza_sede = Q(Appartenenza.query_attuale(
            sede__in=sedi
        ).via("appartenenze"), )

        # 2. Iscritto confermato a un corso base presso una mia sede
        q_iscritto_corso_base_mia_sede = Q(PartecipazioneCorsoBase.con_esito(
            PartecipazioneCorsoBase.ESITO_OK,
            corso__sede__in=sedi
        ).via("partecipazioni_corsi"))

        # 3. Iscritto in attesa a un corso base presso una mia sede
        q_iscritto_in_attesa_corso_base_mia_sede = Q(PartecipazioneCorsoBase.con_esito(
            PartecipazioneCorsoBase.ESITO_PENDING,
            corso__sede__in=sedi
        ).via("partecipazioni_corsi"))

        self.choices = self.choices.filter(
            q_appartenenza_sede |
            q_iscritto_corso_base_mia_sede |
            q_iscritto_in_attesa_corso_base_mia_sede
        ).order_by('nome', 'cognome', 'codice_fiscale') \
            .distinct('nome', 'cognome', 'codice_fiscale')

        return super(PersonaAutocompletamento, self).choices_for_request()

    def choice_html(self, choice):
        if choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).exists():
            app = choice.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        else:
            app = choice.appartenenze_attuali().first() if choice else None
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
            ("(%s del %s)" % (app.get_membro_display(), app.sede)) if app else '',
        )


class PresidenteAutocompletamento(PersonaAutocompletamento):

    def choices_for_request(self):
        if self.request.user.is_superuser:
            self.choices = Persona.objects.all()
        return super(PersonaAutocompletamento, self).choices_for_request()

    choice_html_format = u'''
        <span class='piu-piccolo'>
            <span class="" data-value="%s"><strong>%s</strong><br />
            Nat%s il %s &mdash;
            <span class="monospace">%s</span><br />
            %s
            </span>
        </span>
    '''

    def choice_html(self, choice):
        app = choice.appartenenze_attuali().first() if choice else None
        sede = choice.sede_riferimento() if choice else None
        return self.choice_html_format % (
            self.choice_value(choice),
            self.choice_label(choice),
            choice.genere_o_a,
            choice.data_nascita.strftime("%d/%m/%Y") if choice.data_nascita else None,
            choice.codice_fiscale,
            sede.nome_completo if sede else ""
        )


class SostenitoreAutocompletamento(PersonaAutocompletamento):
    def choices_for_request(self):
        self.choices = self.choices.filter(
            Appartenenza.query_attuale(membro=Appartenenza.SOSTENITORE).via("appartenenze"))
        return super(SostenitoreAutocompletamento, self).choices_for_request()


class VolontarioSedeAutocompletamento(PersonaAutocompletamento):
    def choices_for_request(self):
        sedi = self.request.user.persona.sedi_deleghe_attuali(tipo__in=(UFFICIO_SOCI, UFFICIO_SOCI_UNITA), espandi=True)
        self.choices = self.choices.filter(
            Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO, sede__in=sedi).via("appartenenze"))
        return super(VolontarioSedeAutocompletamento, self).choices_for_request()


class IscrivibiliCorsiAutocompletamento(PersonaAutocompletamento):
    search_fields = ['codice_fiscale', 'email_contatto', ]

    attrs = {
        'required': False,
        'placeholder': 'Inserisci il codice fiscale o e-mail',
        'data-autocomplete-minimum-characters': 6,
    }

    def choices_for_request(self):
        volontari = self.model.objects.filter(
            Q(Appartenenza.query_attuale(membro=Appartenenza.VOLONTARIO).via("appartenenze")))

        self.choices = self.choices.filter(
            Q(Appartenenza.query_attuale(membro=Appartenenza.SOSTENITORE).via("appartenenze")) |
            Q(aspirante__isnull=False)
        ).exclude(
            pk__in=volontari.values_list('pk', flat=True)
        ).order_by('nome', 'cognome', 'codice_fiscale').distinct('nome', 'cognome', 'codice_fiscale')

        return super(PersonaAutocompletamento, self).choices_for_request()


class SedeAutocompletamento(AutocompletamentoBase):
    search_fields = ['nome', 'genitore__nome', ]
    model = Sede

    def choices_for_request(self):
        self.choices = self.choices.filter(
            attiva=True
        )
        return super(SedeAutocompletamento, self).choices_for_request()


class ComitatoAutocompletamento(SedeAutocompletamento):
    search_fields = ['nome', 'genitore__nome', ]
    model = Sede

    def choices_for_request(self):
        self.choices = self.choices.filter(
            tipo=Sede.COMITATO,
            estensione__in=[NAZIONALE, REGIONALE, PROVINCIALE, LOCALE],
        )
        return super(ComitatoAutocompletamento, self).choices_for_request()


class SedeTrasferimentoAutocompletamento(SedeAutocompletamento):
    search_fields = ['nome', 'genitore__nome', ]
    model = Sede

    def choices_for_request(self):
        self.choices = self.choices.filter(
            tipo=Sede.COMITATO,
            estensione__in=[PROVINCIALE, LOCALE, TERRITORIALE],
        )
        return super(SedeTrasferimentoAutocompletamento, self).choices_for_request()


class SedeNuovoCorsoAutocompletamento(SedeAutocompletamento):
    def choices_for_request(self):
        return self.persona.oggetti_permesso(GESTIONE_CORSI_SEDE)


def sedi_di_sangue_regionali():
    my_list = []
    from sangue.models import Sede as SedeSangue
    sedi = SedeSangue.objects.all().distinct('regione')
    nr = 1
    for sede in sedi:
        # print(nr, ' - ', sede.regione)
        # nr += 1
        if 'bolzano' in sede.regione or 'trento' in sede.regione:
            sede.regione = 'Trentino-Alto Adige'
        my_list.append(sede.regione.capitalize())
        # print(nr, ' - ', sede.regione)
        nr += 1
    my_list = list(set(my_list))
    # print(my_list)
    len(my_list)
    return my_list


class SedeRegistraDonazioneAutocompletamento(SedeAutocompletamento):
    search_fields = ['nome', 'genitore__nome', ]
    model = Sede

    def choices_for_request(self):
        self.choices = self.choices.filter(
            tipo=Sede.COMITATO,
            estensione__in=[REGIONALE],
        )
        return super(SedeRegistraDonazioneAutocompletamento, self).choices_for_request()


autocomplete_light.register(PersonaAutocompletamento)
autocomplete_light.register(PresidenteAutocompletamento)
autocomplete_light.register(SostenitoreAutocompletamento)
autocomplete_light.register(VolontarioSedeAutocompletamento)
autocomplete_light.register(IscrivibiliCorsiAutocompletamento)
autocomplete_light.register(SedeAutocompletamento)
autocomplete_light.register(ComitatoAutocompletamento)
autocomplete_light.register(SedeTrasferimentoAutocompletamento)
autocomplete_light.register(SedeNuovoCorsoAutocompletamento)
autocomplete_light.register(SedeRegistraDonazioneAutocompletamento)
