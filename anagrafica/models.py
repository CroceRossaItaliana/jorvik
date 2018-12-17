# coding=utf-8

"""
Questo modulo definisce i modelli del modulo anagrafico di Gaia.

- Persona
- Telefono
- Documento
- Utente
- Appartenenza
- Comitato
- Delega
"""
from datetime import date, timedelta, datetime

import stdnum
from django.conf import settings
from django.db.transaction import atomic
from django.utils import timezone

import codicefiscale
import mptt
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import models
from django.db.models import Q, QuerySet, Avg
from django.utils.functional import cached_property
from django_countries.fields import CountryField
import phonenumbers
from mptt.querysets import TreeQuerySet

from anagrafica.costanti import ESTENSIONE, TERRITORIALE, LOCALE, PROVINCIALE, REGIONALE, NAZIONALE

from anagrafica.permessi.applicazioni import PRESIDENTE, PERMESSI_NOMI, PERMESSI_NOMI_DICT, UFFICIO_SOCI_UNITA, \
    DELEGHE_RUBRICA, DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_1, DELEGATO_OBIETTIVO_4, \
    RESPONSABILE_FORMAZIONE, DELEGATO_OBIETTIVO_6, DELEGATO_OBIETTIVO_5, RESPONSABILE_AUTOPARCO, DELEGATO_CO, \
    DIRETTORE_CORSO, RESPONSABILE_AREA, REFERENTE, OBIETTIVI, COMMISSARIO, CONSIGLIERE, CONSIGLIERE_GIOVANE, VICE_PRESIDENTE
from anagrafica.permessi.applicazioni import UFFICIO_SOCI, PERMESSI_NOMI_DICT
from anagrafica.permessi.costanti import GESTIONE_ATTIVITA, PERMESSI_OGGETTI_DICT, GESTIONE_SOCI, GESTIONE_CORSI_SEDE, GESTIONE_CORSO, \
    GESTIONE_SEDE, GESTIONE_AUTOPARCHI_SEDE, GESTIONE_CENTRALE_OPERATIVA_SEDE
from anagrafica.permessi.delega import delega_permessi, delega_incarichi
from anagrafica.permessi.incarichi import INCARICO_GESTIONE_APPARTENENZE, INCARICO_GESTIONE_TRASFERIMENTI, \
    INCARICO_GESTIONE_ESTENSIONI, INCARICO_GESTIONE_RISERVE, INCARICO_ASPIRANTE
from anagrafica.permessi.persona import persona_ha_permesso, persona_oggetti_permesso, persona_permessi, \
    persona_permessi_almeno, persona_ha_permessi
from anagrafica.validators import valida_codice_fiscale, ottieni_genere_da_codice_fiscale, \
    crea_validatore_dimensione_file, valida_dimensione_file_8mb, valida_dimensione_file_5mb, valida_almeno_14_anni, \
    valida_partita_iva, valida_iban, valida_email_personale
from attivita.models import Turno, Partecipazione
from base.files import PDF, Excel, FoglioExcel
from base.geo import ConGeolocalizzazioneRaggio, ConGeolocalizzazione
from base.models import ModelloSemplice, ModelloAlbero, ConAutorizzazioni, ConAllegati, \
    Autorizzazione, ConVecchioID
from base.stringhe import normalizza_nome, GeneratoreNomeFile
from base.tratti import ConMarcaTemporale, ConStorico, ConProtocollo, ConDelegati, ConPDF
from base.utils import is_list, sede_slugify, UpperCaseCharField, TitleCharField, poco_fa, mezzanotte_24_ieri, \
    mezzanotte_00, mezzanotte_24, concept
from autoslug import AutoSlugField

from curriculum.models import Titolo, TitoloPersonale
from posta.models import Messaggio
from django.apps import apps

from base.notifiche import NOTIFICA_INVIA, NOTIFICA_NON_INVIARE


class Persona(ModelloSemplice, ConMarcaTemporale, ConAllegati, ConVecchioID):
    """
    Rappresenta un record anagrafico in Gaia.
    """

    # Genere
    MASCHIO = 'M'
    FEMMINA = 'F'
    GENERE = (
        (MASCHIO, 'Maschio'),
        (FEMMINA, 'Femmina')
    )

    # Stati
    PERSONA = 'P'
    STATO = (
        (PERSONA,       'Persona'),
    )

    # Costanti
    ETA_GIOVANE = 32
    ETA_MINIMA_SOCIO = 14

    # Informazioni anagrafiche
    nome = TitleCharField("Nome", max_length=64, db_index=True)
    cognome = TitleCharField("Cognome", max_length=64, db_index=True)
    codice_fiscale = UpperCaseCharField("Codice Fiscale", max_length=16, blank=False,
                                        unique=True, db_index=True, validators=[valida_codice_fiscale, ])
    data_nascita = models.DateField("Data di nascita", db_index=True, null=True)
    genere = models.CharField("Sesso", max_length=1, choices=GENERE, db_index=True)

    # Stato
    stato = models.CharField("Stato", max_length=1, choices=STATO, default=PERSONA, db_index=True)

    # Informazioni anagrafiche aggiuntive - OPZIONALI (blank=True o default=..)
    comune_nascita = models.CharField("Comune di Nascita", max_length=64, blank=True)
    provincia_nascita = models.CharField("Provincia di Nascita", max_length=2, blank=True)
    stato_nascita = CountryField("Stato di nascita", default="IT")
    indirizzo_residenza = models.CharField("Indirizzo di residenza", max_length=512, null=True)
    comune_residenza = models.CharField("Comune di residenza", max_length=64, null=True)
    provincia_residenza = models.CharField("Provincia di residenza", max_length=2, null=True)
    stato_residenza = CountryField("Stato di residenza", default="IT")
    cap_residenza = models.CharField("CAP di Residenza", max_length=16, null=True)
    email_contatto = models.EmailField("Email di contatto", max_length=255, blank=True,
                                       validators=[valida_email_personale])
    note = models.TextField("Note aggiuntive", max_length=10000, blank=True, null=True,)

    avatar = models.ImageField("Avatar", blank=True, null=True,
                               upload_to=GeneratoreNomeFile('avatar/'),
                               validators=[valida_dimensione_file_5mb])


    # Privacy

    POLICY_PUBBLICO = 9
    POLICY_REGISTRATI = 7
    POLICY_SEDE = 5
    POLICY_RISTRETTO = 3

    POLICY = (
        (POLICY_PUBBLICO, "Pubblico, inclusi utenti non registrati"),
        (POLICY_REGISTRATI, "Solo utenti registrati di Gaia"),
        (POLICY_SEDE, "A tutti i membri della mia Sede CRI"),
        (POLICY_RISTRETTO, "Ai Responsabili della mia Sede CRI"),
    )

    privacy_contatti = models.SmallIntegerField(choices=POLICY, default=POLICY_SEDE, db_index=True,
                                                help_text="A chi mostrare il mio indirizzo e-mail e i miei numeri "
                                                          "di telefono.")
    privacy_curriculum = models.SmallIntegerField(choices=POLICY, default=POLICY_RISTRETTO, db_index=True,
                                                  help_text="A chi mostrare il mio curriculum (competenze pers., "
                                                            "patenti, titoli di studio e CRI)")
    privacy_deleghe = models.SmallIntegerField(choices=POLICY, default=POLICY_RISTRETTO, db_index=True,
                                               help_text="A chi mostrare i miei incarichi, come presidenze, "
                                                         "referenze attività, deleghe, ecc.")

    iv = models.BooleanField(verbose_name="Infermiera V.", default=False, db_index=True)
    cm = models.BooleanField(verbose_name="Corpo Militare", default=False, db_index=True)

    CONOSCENZA_SITI = "SI"
    CONOSCENZA_FACEBOOK = "FB"
    CONOSCENZA_TWITTER = "TW"
    CONOSCENZA_NEWSLETTER = "NW"
    CONOSCENZA_TV = "TV"
    CONOSCENZA_RADIO = "RA"
    CONOSCENZA_GIORNALI = "GI"
    CONOSCENZA_AMICO = "AM"
    CONOSCENZA_AFFISSIONI = "AF"
    CONOSCENZA_EVENTI = "EV"
    CONOSCENZA_SERVIZI = "SE"
    CONOSCENZA_ALTRO = "AL"
    CONOSCENZA = (
        (CONOSCENZA_SITI, "Siti web della Croce Rossa Italiana"),
        (CONOSCENZA_FACEBOOK, "Facebook"),
        (CONOSCENZA_TWITTER, "Twitter"),
        (CONOSCENZA_NEWSLETTER, "Newsletter"),
        (CONOSCENZA_TV, "TV o Web TV"),
        (CONOSCENZA_RADIO, "Radio"),
        (CONOSCENZA_GIORNALI, "Giornali (online o cartacei)"),
        (CONOSCENZA_AMICO, "Da un amico, collega o familiare"),
        (CONOSCENZA_AFFISSIONI, "Affissioni (locandine, manifesti, ecc.)"),
        (CONOSCENZA_EVENTI, "Eventi organizzati dalla CRI (es. stand informativi, manifestazioni, open day, ecc.)"),
        (CONOSCENZA_SERVIZI, "Partecipazione ad attività e/o fruizione di servizi erogati dalla CRI (es. corsi di "
                             "formazione, servizi sanitari, servizi sociali, ecc.)"),
        (CONOSCENZA_ALTRO, "Altro"),
    )
    conoscenza = models.CharField(max_length=2, choices=CONOSCENZA, default=None, blank=False, null=True, db_index=True,
                                  help_text="Come sei venuto/a a conoscenza delle opportunità di "
                                            "volontariato della CRI?")

    @property
    def nome_completo(self):
        """
        Restituisce il nome e cognome
        :return: "Nome Cognome".
        """
        return normalizza_nome(self.nome + " " + self.cognome)

    @property
    def cognome_nome_completo(self):
        """
        Restituisce il nome e cognome
        :return: "Nome Cognome".
        """
        return normalizza_nome(self.cognome + " " + self.nome)


    # Q: Qual e' l'email di questa persona?
    # A: Una persona puo' avere da zero a due indirizzi email.
    #    - Persona.email_contatto e' quella scelta dalla persona per il contatto.
    #    - Persona.utenza.email (o Persona.email_utenza) e' quella utilizzata per accedere al sistema.
    #    - Persona.email puo' essere usato per ottenere, in ordine, l'email di contatto,
    #       oppure, se non impostata, quella di utenza. Se nemmeno una utenza e' disponibile,
    #       viene ritornato None.

    @property
    def email(self):
        """
        Restituisce l'email preferita dalla persona.
        Se impostata, restituisce l'email di contatto, altrimento l'email di utenza.
        :return:
        """
        if self.email_contatto:
            return self.email_contatto
        return self.email_utenza

    @property
    def genere_codice_fiscale(self):
        return ottieni_genere_da_codice_fiscale(self.codice_fiscale)

    @property
    def email_firma(self):
        """
        La firma e-mail dell'utente (es. "Mario Rossi <mario@rossi.it>")
        :return: Stringa.
        """
        return self.nome_completo + " <" + self.email_contatto + ">"

    @property
    def email_utenza(self):
        """
        Restituisce l'email dell'utenza, se presente.
        :return: Email o None
        """
        if hasattr(self, 'utenza'):
            return self.utenza.email
        return None

    @property
    def admin(self):
        """
        Controlla se l'utente e' admin.
        :return: True se admin, False altrimenti.
        """
        return hasattr(self, 'utenza') and self.utenza.is_staff

    @property
    def sospeso(self):
        return ProvvedimentoDisciplinare.query_attuale(persona=self,
                                                       tipo=ProvvedimentoDisciplinare.SOSPENSIONE).exists()
    @property
    def in_riserva(self):
        return Riserva.query_attuale(Riserva.con_esito_ok().q, persona=self).exists()

    @property
    def ultimo_tesserino(self):
        return self.tesserini.all().order_by("creazione").last()

    def __str__(self):
        return self.nome_completo

    class Meta:
        verbose_name_plural = "Persone"
        app_label = 'anagrafica'
        index_together = [
            ['nome', 'cognome'],
            ['nome', 'cognome', 'codice_fiscale'],
            ['id', 'nome', 'cognome', 'codice_fiscale'],
        ]
        permissions = (
            ('view_persona', "Can view persona"),
            ('transfer_persona', "Can transfer persona"),
        )

    # Q: Qual e' il numero di telefono di questa persona?
    # A: Una persona puo' avere da zero ad illimitati numeri di telefono.
    #    - Persona.numeri_telefono ottiene l'elenco di oggetti Telefono.
    #    - Per avere un elenco di numeri di telefono formattati, usare ad esempio
    #       numeri = [str(x) for x in Persona.numeri_telefono]
    #    - Usare Persona.aggiungi_numero_telefono per aggiungere un numero di telefono.
    def numeri_pubblici(self):
        numeri_servizio = self.numeri_telefono.filter(servizio=True)
        if numeri_servizio.exists():
            return numeri_servizio
        return self.numeri_telefono.all()

    def deleghe_attuali(self, al_giorno=None, solo_attive=True, **kwargs):
        """
        Ritorna una ricerca per le deleghe che son attuali.
        """
        deleghe = self.deleghe.filter(Delega.query_attuale(al_giorno=al_giorno).q, **kwargs)
        if solo_attive:
            deleghe = deleghe.filter(stato=Delega.ATTIVA)
        return deleghe

    def deleghe_attuali_rubrica(self, al_giorno=None, **kwargs):
        """
        Ritorna una ricerca per le deleghe che son attuali.
        """
        return self.deleghe.filter(Delega.query_attuale(al_giorno=al_giorno).q,
                                   tipo__in=DELEGHE_RUBRICA,
                                   **kwargs)

    def sedi_deleghe_attuali(self, al_giorno=None, espandi=False, pubblici=False, deleghe=None, **kwargs):
        sedi = Sede.objects.none()
        tipo_sede = ContentType.objects.get_for_model(Sede)
        if not deleghe:
            deleghe = self.deleghe_attuali(al_giorno=al_giorno, oggetto_tipo=tipo_sede)
        for d in deleghe:
            if d.oggetto_tipo != tipo_sede and hasattr(d.oggetto, 'sede'):
                oggetto = d.oggetto.sede
            else:
                oggetto = d.oggetto
            if espandi:
                pks = [x.pk for x in oggetto.espandi(includi_me=True, pubblici=pubblici)]
            else:
                pks = [oggetto.pk]

            sedi |= Sede.objects.filter(pk__in=pks)
        return sedi

    def aggiungi_numero_telefono(self, numero, servizio=False, paese="IT"):
        """
        Aggiunge un numero di telefono per la persona.
        :param numero: Il numero di telefono.
        :param servizio: Vero se il numero e' di servizio. Default False.
        :param paese: Suggerimento per il paese. Default "IT".
        :return: True se l'inserimento funziona, False se il numero e' mal formattato.
        """
        try:
            n = phonenumbers.parse(numero, paese)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False
        f = phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164)
        t = Telefono(persona=self, numero=f, servizio=servizio)
        try:
            t.save()
        except:
            return False
        return True

    def appartenenze_attuali(self, **kwargs):
        """
        Ottiene il queryset delle appartenenze attuali e confermate.
        """
        return self.appartenenze.filter(Appartenenza.query_attuale(**kwargs).q).select_related('sede')

    def appartenenze_pendenti(self, **kwargs):
        """
        Ottiene il queryset delle appartenenze non confermate.
        """
        return self.appartenenze.filter(confermata=False, **kwargs).select_related('sede')

    def prima_appartenenza(self, **kwargs):
        """
        Ottiene la prima appartenenza, se esistente.
        """
        return self.appartenenze.filter(confermata=True, **kwargs).order_by('inizio').first()

    def appartenenze_per_presidente(self, presidente):
        """
        Ottiene il queryset delle appartenenze attuali e confermate, in base al Presidente
        """
        return [(appartenenza.pk, appartenenza.membro_a_stringa()) for appartenenza in self.appartenenze_attuali() \
                if presidente in appartenenza.sede.delegati_attuali() \
                or presidente in appartenenza.sede.genitore.delegati_attuali()]

    def ingresso(self, **kwargs):
        """
        Ottiene la data di ingresso della persona o None se non disponibile.
        """
        try:
            a = self.prima_appartenenza(**kwargs)

        except ObjectDoesNotExist:
            return None

        return a.inizio

    def membro_di(self, sede, **kwargs):
        """
        Controlla se la persona e' membro attuale e confermato di un dato sede.
        E' possibile aggiungere dati come membro=VOLONTARIO,...
        """
        return sede.ha_membro(persona=self, **kwargs)

    def membro(self, membro, **kwargs):
        """
        Controlla se la persona ha appartenenza come mebro tipo specificato

        es. if p.membro(DIPENDENTE):
              Print("Sei anche dipendente...")
        """
        return self.appartenenze_attuali(membro=membro, **kwargs).exists()

    def membro_sotto(self, sede, **kwargs):
        """
        Controlla se la persona e' membro attuale e confermato di un dato sede
        o di uno dei suoi figli diretti.
        """
        return self.membro_di(self, sede, includi_figli=True, **kwargs)

    def sedi_attuali(self, **kwargs):
        """
        Ottiene queryset di Sede di cui fa parte
        """
        return Sede.objects.filter(pk__in=[x.sede.pk for x in self.appartenenze_attuali(**kwargs)])

    def titoli_personali_confermati(self):
        """
        Ottiene queryset per TitoloPersonale con conferma approvata.
        """
        return self.titoli_personali.filter(confermata=True).select_related('titolo')

    def titoli_confermati(self):
        """
        Ottiene queryset per Titolo con conferma approvata.
        """
        return [x.titolo for x in self.titoli_personali_confermati()]

    def fototessera_attuale(self):
        """
        Ottiene la fototessera confermata se presente.
        Se non esiste, lancia ObjectDoesNotExist.
        """
        return self.fototessere.filter(confermata=True).latest('ultima_modifica')

    def fototessere_pending(self):
        """
        Ottiene il queryset di fototessere in attesa di conferma.
        :return: QuerySet<Fototessera>
        """
        return Fototessera.con_esito_pending().filter(persona=self)

    @property
    def ha_aspirante(self):
        """
        Controlla se la persona ha un oggetto aspirante, altrimenti ritora False.
        """
        try:
            return self.aspirante is not None
        except ObjectDoesNotExist:
            return False

    @property
    def eta(self, al_giorno=None):
        """
        Ottiene l'eta' in anni del volontario.
        """
        if not self.data_nascita:
            return 0
        al_giorno = al_giorno or date.today()
        return al_giorno.year - self.data_nascita.year - ((al_giorno.month, al_giorno.day) < (self.data_nascita.month, self.data_nascita.day))

    @classmethod
    @concept
    def query_eta_minima(cls, eta, al_giorno=None):
        al_giorno = al_giorno or date.today()
        data_nascita_massima = al_giorno.replace(year=al_giorno.year - eta)
        return Q(data_nascita__lte=data_nascita_massima)

    @classmethod
    @concept
    def query_eta_massima(cls, eta, al_giorno=None):
        al_giorno = al_giorno or date.today()
        data_nascita_minima = al_giorno.replace(year=al_giorno.year - eta)
        return Q(data_nascita__gte=data_nascita_minima)

    @property
    def giovane(self, **kwargs):
        return self.eta < self.ETA_GIOVANE

    def ultimo_accesso_testo(self):
        """
        Ottiene l'ultimo accesso in testo, senza ledere la privacy.
        """
        try:
            if not self.utenza.ultimo_accesso:
                return "Mai"

        except:
            return "Mai"

        if self.utenza.ultimo_accesso < datetime.now() - timedelta(days=5):
            return "Recentemente"

        if self.utenza.ultimo_accesso < datetime.now() - timedelta(days=31):
            return "Nell'ultimo mese"

        return "Più di un mese fà"

    @property
    def volontario(self, **kwargs):
        """
        Controlla se membro volontario
        """
        return self.membro(Appartenenza.VOLONTARIO, **kwargs)

    @property
    def ordinario(self, **kwargs):
        """
        Controlla se membro ordinario
        """
        return self.membro(Appartenenza.ORDINARIO, **kwargs)

    @property
    def dipendente(self, **kwargs):
        """
        Controlla se membro dipendente
        """
        return self.membro(Appartenenza.DIPENDENTE, **kwargs)

    @property
    def est_donatore(self, **kwargs): # Nome differente perché confligge con il descrittore della relazione inversa con Donatore
        """
        Controlla se membro donatore
        """
        return self.membro(Appartenenza.DONATORE, **kwargs)

    @property
    def militare(self, **kwargs):
        """
        Controlla se membro militare
        """
        return self.membro(Appartenenza.MILITARE, **kwargs)

    @property
    def infermiera(self, **kwargs):
        """
        Controlla se membro infermiera
        """
        return self.membro(Appartenenza.INFERMIERA, **kwargs)

    @property
    def sostenitore(self, **kwargs):
        """
        Controlla se membro sostenitore
        """
        return self.membro(Appartenenza.SOSTENITORE, **kwargs)

    @property
    def applicazioni_disponibili(self):
        lista = []

        if self.volontario:
            lista += [('/utente/', 'Volontario', 'fa-user')]
        elif not hasattr(self, 'aspirante'):
            lista += [('/utente/', 'Utente', 'fa-user')]

        if hasattr(self, 'aspirante'):
            if self.dipendente:
                lista += [('/utente/', 'Utente', 'fa-user')]
            else:
                lista += [('/aspirante/', 'Aspirante', 'fa-user', self.aspirante.corsi().count())]

        if self.volontario:
            lista += [('/attivita/', 'Attività', 'fa-calendar')]

        lista += [('/posta/', 'Posta', 'fa-envelope')]

        if self.ha_pannello_autorizzazioni:
            lista += [('/autorizzazioni/', 'Richieste', 'fa-user-plus', self.autorizzazioni_in_attesa().count())]

        if self.ha_permesso(GESTIONE_SEDE):
            lista += [('/presidente/', 'Sedi', 'fa-home')]

        if self.ha_permesso(GESTIONE_SOCI):
            lista += [('/us/', 'Soci', 'fa-users')]

        if self.ha_permesso(GESTIONE_AUTOPARCHI_SEDE):
            lista += [('/veicoli/', "Veicoli", "fa-car")]

        if self.ha_permesso(GESTIONE_CENTRALE_OPERATIVA_SEDE):
            lista += [('/centrale-operativa/', "CO", "fa-compass")]

        if self.ha_permesso(GESTIONE_CORSO) or self.ha_permesso(GESTIONE_CORSI_SEDE):
            lista += [('/formazione/', 'Formazione', 'fa-graduation-cap')]

        tipi = []
        for d in self.deleghe_attuali():
            if d.tipo in tipi:
                continue
            tipi.append(d.tipo)
            #lista += [(APPLICAZIONI_SLUG_DICT[d.tipo], PERMESSI_NOMI_DICT[d.tipo])]
        lista += [('/articoli/', 'Articoli', 'fa-newspaper-o')]
        lista += [('/documenti/', 'Documenti', 'fa-folder')]
        return lista


    def oggetti_permesso(self, permesso, al_giorno=None,
                         solo_deleghe_attive=True):
        """
        Dato un permesso, ritorna un queryset agli oggetti che sono coperti direttamente
        dal permesso. Es.: GESTIONE_SOCI -> Elenco dei Comitati in cui si ha gestione dei soci.
        :param permesso: Permesso singolo.
        :param al_giorno: Data di verifica.
        :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
        :return: QuerySet. Se permesso non valido, QuerySet vuoto o None (EmptyQuerySet).
        """
        permessi = persona_oggetti_permesso(self, permesso, al_giorno=al_giorno,
                                            solo_deleghe_attive=solo_deleghe_attive)
        if isinstance(permessi, QuerySet):
            return permessi

        else:
            return apps.get_model(PERMESSI_OGGETTI_DICT[permesso][0],
                                  PERMESSI_OGGETTI_DICT[permesso][1]).objects.none()

    def permessi(self, oggetto, al_giorno=None):
        """
        Ritorna il livello di permessi che si ha su un qualunque oggetto.

        Se non e' necessario conoscere il livello, ma si vuole controllare se si hanno
         abbastanza permessi, la funzione booleanea Persona.permessi_almeno(oggetto, minimo)
         dovrebbe essere preferita, in quanto ottimizzata (ie. smette di ricercare una volta
         superato il livello minimo di permesso che si sta cercando).

        :param oggetto: Oggetto qualunque.
        :param al_giorno:  Data di verifica.
        :return: Intero. NESSUNO...COMPLETO
        """
        return persona_permessi(self, oggetto, al_giorno=al_giorno)

    def permessi_almeno(self, oggetto, minimo, al_giorno=None, solo_deleghe_attive=True):
        """
        Controlla se ho i permessi minimi richiesti specificati su un dato oggetto.

        :param oggetto: Oggetto qualunque.
        :param minimo: Oggetto qualunque.
        :param al_giorno:  Data di verifica.
        :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
        :return: True se permessi >= minimo, False altrimenti
        """
        return persona_permessi_almeno(self, oggetto, minimo=minimo, al_giorno=al_giorno,
                                       solo_deleghe_attive=solo_deleghe_attive)

    def ha_permesso(self, permesso, al_giorno=None, solo_deleghe_attive=True):
        """
        Dato un permesso, ritorna true se il permesso e' posseduto.
        :param permesso: Permesso singolo.
        :param al_giorno: Data di verifica.
        :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
        :return: True se il permesso e' posseduto. False altrimenti.
        """
        return persona_ha_permesso(self, permesso, al_giorno=al_giorno,
                                   solo_deleghe_attive=solo_deleghe_attive)

    def ha_permessi(self, *permessi, solo_deleghe_attive=True):
        """
        Dato un elenco di permessi, ritorna True se tutti i permessi sono posseduti.
        :param permessi: Elenco di permessi.
        :param solo_deleghe_attive: True se deve usare solo le deleghe attive per il calcolo del permesso. False altrimenti.
        :return: True se tutti i permessi sono posseduti. False altrimenti.
        """
        return persona_ha_permessi(self, *permessi, solo_deleghe_attive=solo_deleghe_attive)

    def invia_email_benvenuto_registrazione(self, tipo='aspirante'):
        """
        Invia una email di benvenuto in seguito alla registrazione.
        :param tipo: Stringa 'aspirante' o 'volontario'.
        """
        from posta.models import Messaggio

        Messaggio.costruisci_e_invia(
            oggetto="Benvenut%s su Gaia!" % (self.genere_o_a,),
            modello="email_benvenuto_%s_registrazione.html" % (tipo,),
            corpo={
                'nome': self.nome_completo,
            },
            destinatari=[self]
        )

    def posta_in_arrivo(self):
        """
        Ottiene il queryset della posta in arrivo per la Persona.
        :return: Queryset della posta in arrivo.
        """
        return Messaggio.objects.filter(oggetti_destinatario__persona=self).order_by('-creazione')

    def posta_in_uscita(self):
        """
        Ottiene il queryset della posta in uscita per la Persona.
        :return: Queryset della posta in uscita.
        """
        return Messaggio.objects.filter(mittente=self).order_by('-creazione')

    def da_aspirante_a_volontario(self, sede, inizio=None, mittente=None):
        """
        Questa funzione trasforma la Persona da aspirante in volontario.
        - Rimuove l'oggetto aspirante associato alla persona,
        - Crea una nuova appartenenza di tipo VOLONTARIO presso la Sede.
        """

        # Cancella tutti gli oggetti aspirante.
        from formazione.models import Aspirante
        Aspirante.objects.filter(persona=self).delete()

        if self.volontario:
            return

        inizio = inizio or poco_fa()

        # Se precedentemente era ordinario, la sua appartenenza come tale finisce qui.
        Appartenenza.query_attuale(persona=self, membro__in=Appartenenza.MEMBRO_SOCIO).update(fine=inizio)

        # Crea la nuova appartenenza.
        appartenenza = Appartenenza(
            inizio=inizio,
            membro=Appartenenza.VOLONTARIO,
            persona=self,
            sede=sede,
        )
        appartenenza.save()

    def partecipazione_corso_base(self):
        """
        Ritorna la partecipazione confermata al corso base in corso, se esistente,
         altrimenti None.
        :return:
        """
        from formazione.models import PartecipazioneCorsoBase, CorsoBase
        return PartecipazioneCorsoBase.con_esito_ok().filter(persona=self, corso__stato=CorsoBase.ATTIVO).first()

    @property
    def volontario_da_meno_di_un_anno(self):
        """
        Controlla se questo utente è diventato volontario nell'anno corrente
        """
        if self.volontario:
            inizio_anno = poco_fa().replace(month=1, day=1)
            r = self.appartenenze_attuali().filter(membro=Appartenenza.VOLONTARIO, inizio__gte=inizio_anno)
            return r.exists()

    @property
    def url(self):
        return "/profilo/%d/" % (self.pk,)

    @property
    def url_profilo_anagrafica(self):
        return "%sanagrafica/" % (self.url,)

    @property
    def url_profilo_foto(self):
        return "%sfotografie/" % (self.url,)

    @property
    def url_profilo_fototessera(self):
        return "%sfototessera/" % (self.url,)

    @property
    def url_profilo_turni(self):
        return "%sturni/" % (self.url,)

    @property
    def url_profilo_turni_foglio(self):
        return "%sturni/foglio/" % (self.url,)

    @property
    def url_profilo_credenziali(self):
        return "%scredenziali/" % (self.url,)

    @property
    def url_profilo_appartenenze(self):
        return "%sappartenenze/" % (self.url,)

    @property
    def url_profilo_deleghe(self):
        return "%sdeleghe/" % (self.url,)

    @property
    def url_profilo_quote(self):
        return "%squote/" % (self.url,)

    @property
    def url_contatti(self):
        return "/utente/contatti/"

    @property
    def messaggio_url(self):
        return self.url + "messaggio/"

    @property
    def url_messaggio(self):
        return self.messaggio_url

    @property
    def link(self):
        return "<a href='" + str(self.url) + "'>" + str(self.nome_completo) + "</a>"

    def calendario_turni(self, inizio, fine):
        """
        Ritorna il QuerySet per i turni da mostrare in calendario alla Persona.
        :param inizio: datetime.date per il giorno di inizio (incl.)
        :param fine: datetime.date per il giorno di fine (incl.)
        :return: QuerySet per Turno
        """
        from attivita.models import Attivita
        sedi = self.sedi_attuali(membro__in=Appartenenza.MEMBRO_ATTIVITA)
        return Turno.objects.filter(
            # Attivtia organizzate dai miei comitati
            Q(attivita__sede__in=sedi)
            # Attivita aperte ai miei comitati
            | Q(attivita__estensione__in=Sede.objects.get_queryset_ancestors(sedi, include_self=True))
            # Attivita che gesticsco
            | Q(attivita__in=self.oggetti_permesso(GESTIONE_ATTIVITA))
            , inizio__gte=inizio, fine__lt=(fine + timedelta(1)),
              attivita__stato=Attivita.VISIBILE,
        ).order_by('inizio')

    @property
    def ha_pannello_autorizzazioni(self):
        """
        Ritorna True se il pannello autorizzazioni deve essere mostrato per l'utente.
        False altrimenti.
        """
        return (self.deleghe_attuali().exists() or
                self.autorizzazioni_in_attesa().exists() or
                INCARICO_ASPIRANTE in dict(self.incarichi()))

    def incarichi(self):

        if hasattr(self, 'aspirante'):
            incarichi_persona = {INCARICO_ASPIRANTE: [(self.__class__.objects.filter(pk=self.pk),
                                                       self.creazione)]}

        else:
            incarichi_persona = {}

        for delega in self.deleghe_attuali():
            incarichi_delega = delega.espandi_incarichi()

            for incarico in incarichi_delega:
                if not incarico[0] in incarichi_persona:
                    incarichi_persona.update({incarico[0]: [(incarico[1], delega.inizio)]})

                else:
                    incarichi_persona[incarico[0]].append((incarico[1], delega.inizio))

        return incarichi_persona.items()

    def autorizzazioni(self):
        """
        Ritorna tutte le autorizzazioni firmabili da questo utente.
        :return: QuerySet<Autorizzazione>.
        """
        a = Autorizzazione.objects.none()
        for incarico in self.incarichi():
            for potere in incarico[1]:

                if isinstance(potere[0], QuerySet):
                    q_id = Q(destinatario_oggetto_id__in=potere[0].values_list('id', flat=True),
                             destinatario_oggetto_tipo=ContentType.objects.get_for_model(potere[0].model))

                else:  # Se modello instanziato
                    q_id = Q(destinatario_oggetto_id=potere[0].pk,
                             destinatario_oggetto_tipo=ContentType.objects.get_for_model(potere[0]))

                a |= Autorizzazione.objects.filter(
                    q_id,
                    destinatario_ruolo=incarico[0], creazione__gte=potere[1],
                )

        a = a.distinct('progressivo', 'oggetto_tipo_id', 'oggetto_id',)
        return Autorizzazione.objects.filter(
            pk__in=a.values_list('id', flat=True)
        )

    def _autorizzazioni_in_attesa(self):
        """
        Ritorna tutte le autorizzazioni firmabili da qesto utente e in attesa di firma.
        :return: QuerySet<Autorizzazione>
        """
        return self.autorizzazioni().filter(necessaria=True)

    def autorizzazioni_in_attesa(self):
        """
        Ritorna tutte le autorizzazioni firmabili da qesto utente e in attesa di firma.
        :return: QuerySet<Autorizzazione>
        """
        return self._autorizzazioni_in_attesa().order_by('creazione')

    @cached_property
    def trasferimenti_in_attesa(self):
        """
        Ritorna tutti i trasferimenti firmabili da qesto utente e in attesa di firma,
        :return: QuerySet<Autorizzazione>
        """
        return self.autorizzazioni_in_attesa().filter(oggetto_tipo=ContentType.objects.get_for_model(Trasferimento))

    @cached_property
    def trasferimenti_automatici(self):
        """
        Ritorna tutti i trasferimenti firmabili da qesto utente e in attesa di firma, con approvazione automatica
        :return: QuerySet<Autorizzazione>
        """
        return self.trasferimenti_in_attesa.filter(scadenza__isnull=False).exclude(tipo_gestione=Autorizzazione.MANUALE)

    @cached_property
    def trasferimenti_manuali(self):
        """
        Ritorna tutti i trasferimenti firmabili da qesto utente e in attesa di firma, senza approvazione automatica
        :return: QuerySet<Autorizzazione>
        """
        return self.trasferimenti_in_attesa.filter(tipo_gestione=Autorizzazione.MANUALE)

    @cached_property
    def estensioni_da_autorizzare(self):
        return self.autorizzazioni_in_attesa().filter(oggetto_tipo=ContentType.objects.get_for_model(Estensione))

    def deleghe_anagrafica(self):
        """
        Ritora un queryset di tutte le deleghe attuali alle persone che sono
        autorizzate a gestire la scheda anagrafica di questa persona.
        :return: QuerySet<Delega>
        """
        i = Delega.objects.none()
        for s in self.sedi_attuali(membro__in=Appartenenza.MEMBRO_DIRETTO):
            i |= s.deleghe_attuali().filter(tipo__in=[PRESIDENTE, UFFICIO_SOCI, UFFICIO_SOCI_UNITA])
            i |= s.comitato.deleghe_attuali().filter(tipo__in=[PRESIDENTE, UFFICIO_SOCI])
        return i

    @property
    def trasferimento(self):
        """
        Ritorna Trasferimento in attesa di conferma, se applicabile.
        Altrimenti, None.
        :return: Trasferimento in attesa, altrimenti None.
        """
        return self.trasferimenti.all().filter(
            Q(pk__in=Trasferimento.con_esito_pending().filter(persona=self))  # O con esito pending
        ).first()

    def estensioni_attuali(self):
        return self.estensioni.all().filter(
            Q(pk__in=Estensione.con_esito_ok()),
            Appartenenza.query_attuale().via("appartenenza"),
        )

    def estensioni_in_attesa(self):
        return self.estensioni.all().filter(
            Q(pk__in=Estensione.con_esito_pending())
        )

    def estensioni_attuali_e_in_attesa(self):
        return self.estensioni_attuali() | self.estensioni_in_attesa()

    def trasferimento_massivo(self, sede, firmatario, motivazione, data):
        if not sede:
            return 'Non è stata specificata la sede'
        if not firmatario:
            return 'Non è presente alcun firmatario'
        if not motivazione:
            return 'Non è stata indicata la motivazione'
        if not data:
            return 'Non è stata indicata data di trasferimento'
        try:
            if not isinstance(sede, Sede):
                sede = Sede.objects.get(pk=int(sede))
        except (ValueError, Sede.DoesNotExist):
            return False
        data_inizio = datetime(data.year, data.month, data.day)
        if self.volontario and self.sede_riferimento() != sede:
            trasferimento = Trasferimento.objects.create(
                destinazione=sede,
                persona=self,
                richiedente=firmatario,
                motivo=motivazione,
                massivo=True
            )
            trasferimento.autorizzazione_concessa(modulo=None, auto=True, notifiche_attive=False, data=data_inizio)
            return trasferimento.appartenenza
        else:
            return 'La persone non è un volontario o è già nella sede indicata'

    def espelli(self):
        data = poco_fa()
        for appartenenza in self.appartenenze_attuali():
            appartenenza.terminazione = Appartenenza.ESPULSIONE
            appartenenza.fine = mezzanotte_24_ieri(data)
            appartenenza.save()
        self.chiudi_tutto(mezzanotte_24_ieri(data))

    def chiudi_tutto(self, data, da_dipendente=False, mittente_mail=None):
        """
        Chiude tutti i ruoli collegati a fronte di dimissioni / espulsioni / trasferimenti

        Termina:
          * Riserve aperte
          * Estensioni in corso
          * Deleghe (obiettivo, area, attivita, US, autoparco)

        Cancella: (cancellando completamente il record):
          * Partecipazioni a turni non ancora terminati

        Ritira:
          * Autorizzazioni non ancora concesse / negate
        """
        for riserva in self.riserve.filter(Q(fine__isnull=True) | Q(fine__gte=poco_fa())):
            riserva.termina(data=data)

        if not da_dipendente:
            for estensione in self.estensioni_attuali():
                estensione.termina(data=data)

        # Per le attività bisogna attivare dei fallback quindi le gestiamo separatamente
        for delega in self.deleghe_attuali(tipo__in=OBIETTIVI.values()):
            delega.termina(mittente=mittente_mail, data=data)

        for delega in self.deleghe_attuali(tipo=RESPONSABILE_AREA):
            delega.termina(mittente=mittente_mail, data=data)
            if not delega.oggetto.delegati_attuali(al_giorno=data).exists():
                for delegato_obiettivo in Delega.objects.filter(
                    tipo=delega.oggetto.codice_obiettivo,
                    oggetto_tipo=ContentType.objects.get_for_model(Sede),
                    oggetto_id=delega.oggetto.sede_id,
                    inizio__lte=data
                ).filter(Q(fine__isnull=True) | Q(fine__gt=data)):
                    delega.oggetto.aggiungi_delegato(
                        RESPONSABILE_AREA, delegato_obiettivo.persona,
                        inizio=mezzanotte_00(data + timedelta(days=1))
                    )

        for delega in self.deleghe_attuali(tipo=REFERENTE):
            delega.termina(mittente=mittente_mail, data=data)
            if not delega.oggetto.referenti_attuali(al_giorno=data).exists():
                for responsabile_area in delega.oggetto.area.delegati_attuali(al_giorno=data):
                    delega.oggetto.aggiungi_delegato(
                        REFERENTE, responsabile_area,
                        inizio=mezzanotte_00(data + timedelta(days=1))
                    )

        # Tutte le altre deleghe le terminiamo e basta
        for delega in self.deleghe_attuali(solo_attive=False):
            delega.termina(mittente=mittente_mail, data=data)

        if not da_dipendente:
            for partecipazione in self.partecipazioni.filter(turno__fine__gte=poco_fa()):
                partecipazione.delete()

            for richieste in self.autorizzazioni_in_attesa():
                richieste.oggetto.autorizzazioni_ritira()

    def ottieni_o_genera_aspirante(self):
        try:
            return self.aspirante
        except:
            from formazione.models import Aspirante
            a = Aspirante(
                persona=self,
            )
            a.save()
            a.imposta_locazione("%s, %s %s, %s, %s" % (
                self.indirizzo_residenza, self.cap_residenza,
                self.comune_residenza, self.provincia_residenza,
                self.stato_residenza
            ))
            return a

    def sede_riferimento(self, membro=None, **kwargs):
        membro = membro or Appartenenza.MEMBRO_DIRETTO
        return self.sedi_attuali(membro__in=membro, **kwargs).\
            order_by('-appartenenze__inizio').first()

    def sedi_riferimento(self, membro=None, **kwargs):
        membro = membro or Appartenenza.MEMBRO_DIRETTO
        return self.sedi_attuali(membro__in=membro, **kwargs). \
            order_by('-appartenenze__inizio')

    def comitati_riferimento(self, **kwargs):
        sedi = self.sede_riferimento(**kwargs)
        comitati = [x.comitato for x in sedi]
        if comitati:
            return comitati
        return sedi

    def comitato_riferimento(self, **kwargs):
        sede = self.sede_riferimento(**kwargs)
        if sede:
            return sede.comitato
        return sede

    def quote_anno(self, anno, **kwargs):
        from ufficio_soci.models import Quota
        return Quota.objects.filter(
            persona=self,
            anno=anno,
            **kwargs
        )

    @property
    def genere_o_a(self):
        """
        Ritorna 'o' per un uomo, 'a' per una donna.
        """
        genere = self.genere_codice_fiscale or self.genere
        return 'o' if genere == self.MASCHIO else 'a'

    def genera_inizio_codice_fiscale(self):
        try:
            return codicefiscale.build(
                self.cognome, self.nome, self.data_nascita,
                self.genere_codice_fiscale, 'D969'
            )[0:11]
        except:
            return ''

    def codice_fiscale_verosimile(self):
        """
        Controlla se il codice fiscale e' verosimile o meno
        """
        return codicefiscale.isvalid(self.codice_fiscale) and self.genera_inizio_codice_fiscale() in self.codice_fiscale

    def reclamabile_in_sede(self, sede):
        """
        Controlla se la persona e' reclamabile come socio presso una determinata sede.

        :param sede: Sede presso la quale reclamare il socio
        :return: True o False
        """
        if not self.sedi_attuali():
            return True

        regionale = sede.superiore(REGIONALE)

        # I soci ordinari sul proprio regionale possono essere reclamati (ma solo se sono **solo** ordinari)
        if self.appartenenze_attuali().filter(
            sede=regionale,
            membro=Appartenenza.ORDINARIO
        ).exists() and not self.appartenenze_attuali().exclude(
            sede=regionale,
            membro=Appartenenza.ORDINARIO
        ).exists():
            return True

        # I soci sostenitori possono essere reclamati (ma solo se sono **solo** sostenitori)
        if self.appartenenze_attuali().filter(
                membro=Appartenenza.SOSTENITORE
        ).exists() and not self.appartenenze_attuali().exclude(
            membro=Appartenenza.SOSTENITORE
        ).exists():
            return True

        # I dipendenti possono essere reclamati (ma solo se sono **solo** dipendenti)
        if self.appartenenze_attuali().filter(
            membro=Appartenenza.DIPENDENTE
        ).exists() and not self.appartenenze_attuali().exclude(
            membro=Appartenenza.DIPENDENTE
        ).exists():
            return True

        # Se è volontario è possibile reclamarlo previa messa in riserva (gestito altrove)
        if self.appartenenze_attuali().filter(
            membro=Appartenenza.VOLONTARIO
        ).exists() and not self.appartenenze_attuali().exclude(
            membro__in=[Appartenenza.ESTESO,Appartenenza.VOLONTARIO]
        ).exists():
            return True

        # Se è volontario in estensione è possibile reclamarlo previa messa in riserva (gestito altrove)
        if self.appartenenze_attuali().filter(
                membro=Appartenenza.ESTESO
        ).exists() and not self.appartenenze_attuali().exclude(
            membro__in=[Appartenenza.ESTESO,Appartenenza.VOLONTARIO]
        ).exists():
            return True

        return False

    def genera_foglio_di_servizio(self):
        storico = Partecipazione.con_esito_ok().filter(persona=self, stato=Partecipazione.RICHIESTA)\
            .order_by('-turno__inizio')

        anni = storico.dates('turno__inizio', 'year', order='DESC')
        excel = Excel(oggetto=self)

        fogli = []
        # Per ogni anno, crea un foglio
        for anno in anni:
            anno = anno.year
            # Crea il nuovo foglio di lavoro
            foglio = FoglioExcel(
                nome="Anno %d" % (anno,),
                intestazione=(
                    "Attivita", "Localita", "Turno", "Inizio", "Fine",
                )
            )

            # Aggiungi le partecipazioni
            for part in storico.filter(turno__inizio__year=anno):
                foglio.aggiungi_riga(
                    part.turno.attivita.nome,
                    part.turno.attivita.locazione if part.turno.attivita.locazione else 'N/A',
                    part.turno.nome,
                    part.turno.inizio,
                    part.turno.fine,
                )

            fogli.append(foglio)

        for y in fogli:
            excel.aggiungi_foglio(y)

        # Salva file excel e scarica
        excel.genera_e_salva("Foglio di servizio.xlsx")
        return excel

    @property
    def nuovo_presidente(self):
        """
        Ritorna True se la persona e' un nuovo presidente/commissario (meno di un mese)
        """
        un_mese_fa = poco_fa() - timedelta(days=30)
        nuovo_presidente = self.deleghe_attuali(tipo=PRESIDENTE, inizio__gte=un_mese_fa).exists()
        nuovo_commissario = self.deleghe_attuali(tipo=COMMISSARIO, inizio__gte=un_mese_fa).exists()
        return nuovo_presidente or nuovo_commissario

    def oggetti_deleghe(self, *args, tipo=PRESIDENTE, **kwargs):
        deleghe = self.deleghe_attuali(*args, tipo=tipo, **kwargs)
        oggetti = []
        for delega in deleghe:
            oggetti += [delega.oggetto]
        return oggetti

    @property
    def cancellabile(self):
        """
        Ritorna True se la persona puo essere cancellata senza implicazioni.
        """
        from ufficio_soci.models import Quota
        from formazione.models import PartecipazioneCorsoBase
        from attivita.models import Partecipazione
        ha_appartenenza = Appartenenza.objects.filter(persona=self).exists()
        ha_ricevuta = Quota.objects.filter(persona=self).exists()
        ha_partecipazione_corso_base = PartecipazioneCorsoBase.objects.filter(persona=self).exists()
        ha_partecipazione = Partecipazione.objects.filter(persona=self).exists()
        if ha_appartenenza or ha_ricevuta or ha_partecipazione or ha_partecipazione_corso_base:
            return False
        return True

    def appartiene_al_segmento(self, segmento):
        """
        Ritorna True se un utente appartiene ad un segmento
        """
        queryset = Persona.objects.filter(pk=self.pk)
        filtro = segmento.filtro()
        extra_args = segmento.get_extra_filters()
        queryset = filtro(queryset).filter(**extra_args)
        if queryset:
            return queryset.filter(pk=self.pk).exists()
        return False

    @cached_property
    def segmenti_collegati(self):
        """
        Restituisce un elenco di filtri da applicare su un queryset di BaseSegmento
        per applicare i segmenti collegati all'utente, compresi i filtri sulle sedi e sui titoli

        Usato da FiltroSegmentoQuerySet.filtra_per_segmenti

        :return: elenco di condizioni di filtro (usabili come argomenti di un oggetto Q)
        """
        from segmenti.segmenti import SEGMENTI
        utente = Persona.objects.filter(pk=self.pk)
        attivi = []
        titoli = list(self.titoli_confermati())
        sedi_attuali = list(self.sedi_attuali())
        for segmento, filtro in SEGMENTI.items():
            if filtro(utente).exists():
                if segmento == 'A':
                    attivi.append({'segmento': segmento})
                elif segmento == 'AA':
                    for titolo in titoli:
                        attivi.append({'segmento': segmento, 'titolo': titolo})
                else:
                    attivi.append({'segmento': segmento, 'sede__isnull': True})
                    for sede in sedi_attuali:
                        attivi.append({'segmento': segmento, 'sede': sede})
                        attivi.append({'sedi_sottostanti': True, 'sede': sede.genitore})
        return attivi

    def save(self, *args, **kwargs):
        self.nome = normalizza_nome(self.nome)
        self.cognome = normalizza_nome(self.cognome)
        
        # FIxed JO-733
        if self.genere_codice_fiscale and not self.genere:
            self.genere = self.genere_codice_fiscale
            
        super().save(*args, **kwargs)


class Telefono(ConMarcaTemporale, ModelloSemplice):
    """
    Rappresenta un numero di telefono.
    NON USARE DIRETTAMENTE. Usare i metodi in Persona.
    """

    persona = models.ForeignKey(Persona, related_name="numeri_telefono", db_index=True, on_delete=models.CASCADE)
    numero = models.CharField("Numero di telefono", max_length=16)
    servizio = models.BooleanField("Numero di servizio", default=False)

    class Meta:
        verbose_name = "Numero di telefono"
        verbose_name_plural = "Numeri di telefono"
        app_label = 'anagrafica'
        index_together = [
            ['persona', 'servizio'],
        ]
        permissions = (
            ('view_telefono', "Can view Numero di telefono"),
        )

    def _phonenumber(self):
        return phonenumbers.parse(self.numero)

    def __str__(self):
        """
        Ritorna il numero per la visualizzazione nel formato appropriato (Italiano o Internazionale)
        :return: Stringa che rappresenta il numero di telefono.
        """
        n = self._phonenumber()
        if n.country_code == 39:
            return self.nazionale()
        else:
            return self.internazionale()

    def nazionale(self):
        """
        Ritorna il numero formattato come numero nazionale.
        :return: Stringa che rappresenta il numero in formato nazionale.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.NATIONAL)

    def internazionale(self):
        """
        Ritorna il numero formattato come numero internazionale.
        :return: Stringa che rappresenta il numero in formato internazionale.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    def e164(self):
        """
        Ritorna il numero formattato come numero internazionale E.164.
        :return: Stringa che rappresenta il numero in formato internazionale E.164.
        """
        return phonenumbers.format_number(self._phonenumber(), phonenumbers.PhoneNumberFormat.E164)


class Documento(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un documento caricato da un utente.
    """

    # Tipologie di documento caricabili
    CARTA_IDENTITA = 'I'
    PATENTE_CIVILE = 'P'
    PATENTE_CRI = 'S'
    CODICE_FISCALE = 'C'
    ALTRO = 'A'
    TIPO = (
        (CARTA_IDENTITA, 'Carta d\'identità'),
        (PATENTE_CIVILE, 'Patente Civile'),
        (PATENTE_CRI, 'Patente CRI'),
        (CODICE_FISCALE, 'Codice Fiscale'),
        (ALTRO, 'Altro'),
    )

    tipo = models.CharField(choices=TIPO, max_length=1, default=CARTA_IDENTITA, db_index=True)
    persona = models.ForeignKey(Persona, related_name="documenti", db_index=True, on_delete=models.CASCADE)
    file = models.FileField("File", upload_to=GeneratoreNomeFile('documenti/'),
                            validators=[valida_dimensione_file_8mb])

    class Meta:
        verbose_name_plural = "Documenti"
        app_label = 'anagrafica'
        permissions = (
            ("view_documento", "Can view documento"),
        )


class Appartenenza(ModelloSemplice, ConStorico, ConMarcaTemporale, ConAutorizzazioni):
    """
    Rappresenta un'appartenenza di una Persona ad un Sede.
    """

    class Meta:
        verbose_name_plural = "Appartenenze"
        app_label = 'anagrafica'
        index_together = [
            ['persona', 'sede'],
            ['persona', 'inizio', 'fine'],
            ['persona', 'inizio', 'fine', 'membro'],
            ['persona', 'inizio', 'fine', 'membro', 'confermata'],
            ['sede', 'membro'],
            ['inizio', 'fine'],
            ['sede', 'inizio', 'fine'],
            ['sede', 'membro', 'inizio', 'fine'],
            ['id', 'sede', 'membro', 'inizio', 'fine'],
            ['membro', 'confermata'],
            ['membro', 'confermata', 'sede'],
            ['membro', 'confermata', 'inizio', 'fine'],
            ['membro', 'confermata', 'persona'],
            ['confermata', 'persona'],
        ]
        permissions = (
            ("view_appartenenza", "Can view appartenenza"),
        )

    # Tipo di membro
    VOLONTARIO = 'VO'
    ESTESO = 'ES'
    ORDINARIO = 'OR'
    DIPENDENTE = 'DI'
    INFERMIERA = 'IN'
    MILITARE = 'MI'
    DONATORE = 'DO'
    SOSTENITORE = 'SO'

    # Quale tipo di membro puo' partecipare alle attivita'?
    MEMBRO_ATTIVITA = (VOLONTARIO, ESTESO,)

    # Membri sotto il diretto controllo della Sede
    MEMBRO_DIRETTO = (VOLONTARIO, ORDINARIO, DIPENDENTE, INFERMIERA, MILITARE, DONATORE, SOSTENITORE)

    # Membro che puo' essere reclamato da una Sede
    MEMBRO_RECLAMABILE = (VOLONTARIO, ORDINARIO, DIPENDENTE, SOSTENITORE,)

    # Membro che puo' accedere alla rubrica di una Sede
    MEMBRO_RUBRICA = (VOLONTARIO, ORDINARIO, ESTESO, DIPENDENTE,)

    # Membri che possono richiedere il tesserino
    MEMBRO_TESSERINO = (VOLONTARIO,)

    # Membri soci
    MEMBRO_SOCIO = (VOLONTARIO, ORDINARIO,)
    MEMBRO_ANZIANITA = MEMBRO_SOCIO
    MEMBRO_ANZIANITA_ANNI = 2
    MEMBRO_ANZIANITA_ELETTORATO_ATTIVO = 1

    # Membri sotto il diretto controllo di una altra Sede
    MEMBRO_ESTESO = (ESTESO,)

    MEMBRO = (
        (VOLONTARIO, 'Volontario'),
        (ESTESO, 'Volontario in Estensione'),
        (ORDINARIO, 'Socio Ordinario'),
        (SOSTENITORE, 'Sostenitore'),
        (DIPENDENTE, 'Dipendente'),
        #(INFERMIERA, 'Infermiera Volontaria'),
        #(MILITARE, 'Membro Militare'),
        #(DONATORE, 'Donatore Finanziario'),
    )
    PRECEDENZE_MODIFICABILI = (ESTESO,)
    NON_MODIFICABILE = (ESTESO,)
    membro = models.CharField("Tipo membro", max_length=2, choices=MEMBRO, default=VOLONTARIO, db_index=True)

    # Tipo di terminazione
    DIMISSIONE = 'D'
    ESPULSIONE = 'E'
    SOSPENSIONE = 'S'
    TRASFERIMENTO = 'T'
    PROMOZIONE = 'P'
    FINE_ESTENSIONE = 'F'
    TERMINAZIONE = (
        (DIMISSIONE, 'Dimissione'),
        (ESPULSIONE, 'Espulsione'),
        (SOSPENSIONE, 'Sospensione'),
        (TRASFERIMENTO, 'Trasferimento'),
        (PROMOZIONE, 'Promozione'),
        (FINE_ESTENSIONE, 'Fine Estensione'),
    )
    MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI = (FINE_ESTENSIONE, DIMISSIONE, ESPULSIONE)
    terminazione = models.CharField("Terminazione", max_length=1, choices=TERMINAZIONE, default=None, db_index=True,
                                    blank=True, null=True)

    # In caso di trasferimento, o altro, e' possibile individuare quale appartenenza precede
    precedente = models.ForeignKey('self', related_name='successiva', on_delete=models.SET_NULL, default=None,
                                   blank=True, null=True)

    persona = models.ForeignKey("anagrafica.Persona", related_name="appartenenze", db_index=True, on_delete=models.CASCADE)
    sede = models.ForeignKey("anagrafica.Sede", related_name="appartenenze", db_index=True, on_delete=models.PROTECT)
    vecchia_sede = models.ForeignKey("anagrafica.Sede", related_name="appartenenze_vecchie", db_index=True,
                                     null=True, blank=True, on_delete=models.SET_NULL)

    CONDIZIONE_ATTUALE_AGGIUNTIVA = Q(confermata=True)

    RICHIESTA_NOME = "Appartenenza"

    def __str__(self):
        return 'Appartenenza a {}'.format(self.sede)

    @classmethod
    def membro_permesso(cls, estensione=REGIONALE, membro=ORDINARIO):
        """
        Verifica che il tipo di membro sia permesso per la sede.
        """
        if estensione != REGIONALE and membro == cls.ORDINARIO:
            return False
        return True

    def membro_a_stringa(self):
        if self.membro == self.VOLONTARIO:
            return 'Volontario, '+self.sede.nome_completo
        elif self.membro == self.ESTESO:
            return 'Esteso, '+self.sede.nome_completo
        elif self.membro == self.ORDINARIO:
            return 'Ordinario, '+self.sede.nome_completo
        elif self.membro == self.DIPENDENTE:
            return 'Dipendente, '+self.sede.nome_completo
        elif self.membro == self.INFERMIERA:
            return 'Infermiera, '+self.sede.nome_completo
        elif self.membro == self.MILITARE:
            return 'Militare, '+self.sede.nome_completo
        elif self.membro == self.DONATORE:
            return 'Donatore, '+self.sede.nome_completo
        elif self.membro == self.SOSTENITORE:
            return 'Sostenitore, '+self.sede.nome_completo

    def richiedi(self, notifiche_attive=True):
        """
        Richiede di confermare l'appartenenza.
        """
        # Import qui per non essere ricorsivo e rompere il mondo

        self.autorizzazione_richiedi_sede_riferimento(
            self.persona,
            INCARICO_GESTIONE_APPARTENENZE,
            invia_notifica_presidente=notifiche_attive,
            forza_sede_riferimento=self.sede,
        )

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        """
        Questo metodo viene chiamato quando la richiesta viene accettata.
        :return:
        """
        # TODO: Inviare e-mail di autorizzazione concessa!

    def autorizzazione_negata(self, modulo=None, notifiche_attive=True, data=None):
        # TOOD: Fare qualcosa
        self.confermata = False

    def modificabile(self, inizio=None):
        from formazione.models import PartecipazioneCorsoBase

        flag = self.attuale()
        if inizio:
            inizio = inizio.date()
        # Appartenenze come dipendente sono modificabili perché inizio non vincolato a termine di precedente
        if self.membro not in self.NON_MODIFICABILE:
            # Controllo su appartenenza precedente.
            # Nei casi in MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI, l'appartenenza precedente non determina
            # l'apertura di una nuova appartenenza
            if self.precedente and self.precedente.terminazione:
                if self.precedente.terminazione not in self.MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI:
                    flag &= False
                elif inizio:
                    if isinstance(inizio, date):
                        flag &= inizio > self.precedente.fine.date()
                    else:
                        flag &= inizio > self.precedente.fine
            aperte = Appartenenza.objects.filter(persona=self.persona, fine__isnull=True, membro=self.membro).exclude(pk=self.pk)
            if aperte.exists():
                flag &= False
            # Controllo su appartenenze temporalmente precedenti.
            # Nei casi in MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI, l'appartenenza precedente non determina
            # l'apertura di una nuova appartenenza
            modificabili_secondo_terminazione = [membro[0] for membro in self.MEMBRO if membro[0] not in self.PRECEDENZE_MODIFICABILI]
            terminazioni_modificabili = [terminazione[0] for terminazione in self.TERMINAZIONE if terminazione[0] in self.MODIFICABILE_SE_TERMINAZIONI_PRECEDENTI]
            modificabili = [membro[0] for membro in self.MEMBRO if membro[0] in self.PRECEDENZE_MODIFICABILI]
            secondo_terminazione = Appartenenza.objects.filter(persona=self.persona, fine__date__lte=self.inizio, membro__in=modificabili_secondo_terminazione).exclude(pk=self.pk)
            qs_non_modificabili = secondo_terminazione.exclude(terminazione__in=terminazioni_modificabili)
            qs_modificabili = Appartenenza.objects.filter(persona=self.persona, fine__date__lte=self.inizio, membro__in=modificabili).exclude(pk=self.pk) | secondo_terminazione.filter(terminazione__in=terminazioni_modificabili)
            if qs_non_modificabili.exists():
                flag &= False
            if inizio and qs_modificabili.exists():
                flag &= not qs_modificabili.filter(fine__date__gt=inizio).exists()
            qs_corsi = PartecipazioneCorsoBase.objects.filter(persona=self.persona, esito_esame=PartecipazioneCorsoBase.IDONEO)
            if inizio:
                qs_corsi = qs_corsi.filter(corso__data_esame__lte=inizio)
            try:
                data_post = secondo_terminazione.filter(terminazione__in=terminazioni_modificabili).latest('fine')
                qs_corsi = qs_corsi.filter(corso__data_inizio__gt=data_post.fine)
            except Appartenenza.DoesNotExist:
                pass
            if qs_corsi.exists():
                flag = False
            return flag
        else:
            return False

    def appartiene_a(self, sede):
        return self.sede == sede or \
               self.sede.genitore == sede or \
               self.sede == sede.genitore or \
               self.sede.genitore == sede.genitore


class SedeQuerySet(TreeQuerySet):

    def comitati(self):
        """
        Filtra per Comitati.
        """
        return self.filter(estensione__in=[NAZIONALE, REGIONALE, PROVINCIALE, LOCALE])

    def ottieni_comitati(self):
        """
        Filtra per comitati e ottiene i comitati dei presenti
        """
        presenti = self
        comitati_presenti = presenti.filter(estensione__in=[NAZIONALE, REGIONALE, PROVINCIALE, LOCALE])
        territoriali_presenti = presenti.filter(estensione=TERRITORIALE)
        comitati_dei_territoriali_presenti = Sede.objects.filter(figli__in=territoriali_presenti)
        return comitati_presenti | comitati_dei_territoriali_presenti

    def espandi(self, pubblici=False, ignora_disattivi=True, **kwargs):
        """
        Espande il QuerySet.
        Se pubblico, me e tutte le sedi sottostanti.
        Se privato, me e le unita' territoriali incluse.
        :param pubblici: Espand i Comitati pubblici al tutti i Comitati sottostanti.
        :param ignora_disattivi: Ignora le sedi disattive.
        """

        qs = self | Sede.objects.filter(estensione=TERRITORIALE, genitore__in=(self.filter(estensione__in=[PROVINCIALE, LOCALE])))

        if pubblici:
            qs |= self.filter(estensione__in=[NAZIONALE, REGIONALE]).get_descendants(include_self=True)

        if ignora_disattivi:
            qs = qs.filter(attiva=True)

        return qs


class Sede(ModelloAlbero, ConMarcaTemporale, ConGeolocalizzazione, ConVecchioID, ConDelegati):

    class Meta:
        verbose_name = "Sede CRI"
        verbose_name_plural = "Sedi CRI"
        app_label = 'anagrafica'
        index_together = [
            ['estensione', 'tipo'],
            ['genitore', 'estensione'],
            ['attiva', 'estensione'],
            ['attiva', 'tipo'],
            ['lft', 'rght'],
            ['lft', 'rght', 'attiva'],
            ['lft', 'rght', 'attiva', 'estensione'],
            ['lft', 'rght', 'tree_id'],
        ]
        permissions = (
            ("view_sede", "Can view Sede CRI"),
        )

    # Nome gia' presente in Modello Albero

    # Tipologia della sede
    COMITATO = 'C'
    MILITARE = 'M'
    AUTOPARCO = 'A'
    TIPO = (
        (COMITATO, 'Comitato'),
        (MILITARE, 'Sede Militare'),
        (AUTOPARCO, 'Autoparco')
    )

    objects = mptt.managers.TreeManager.from_queryset(SedeQuerySet)()

    estensione = models.CharField("Estensione", max_length=1, choices=ESTENSIONE, db_index=True)
    tipo = models.CharField("Tipologia", max_length=1, choices=TIPO, default=COMITATO, db_index=True)

    # Dati del comitato
    # Nota: indirizzo e' gia' dentro per via di ConGeolocalizzazione
    telefono = models.CharField("Telefono", max_length=64, blank=True)
    fax = models.CharField("FAX", max_length=64, blank=True)
    email = models.EmailField("Indirizzo e-mail", max_length=64, blank=True)
    sito_web = models.URLField("Sito Web", blank=True,
                               help_text="URL completo del sito web, es.: http://www.cri.it/.")
    pec = models.EmailField("Indirizzo PEC", max_length=64, blank=True)
    iban = models.CharField("IBAN", max_length=32, blank=True,
                            help_text="Coordinate bancarie internazionali del "
                                      "C/C della Sede.",
                            validators=[valida_iban])
    codice_fiscale = models.CharField("Codice Fiscale", max_length=32, blank=True)
    partita_iva = models.CharField("Partita IVA", max_length=32, blank=True,
                                   validators=[valida_partita_iva])

    attiva = models.BooleanField("Attiva", default=True, db_index=True)
    __attiva_default = None

    def __init__(self, *args, **kwargs):
        super(Sede, self).__init__(*args, **kwargs)
        # Questo attributo a runtime ci serve per verificare durante il save se il flag "attiva" è stato modficato
        self.__attiva_default = self.attiva

    def save(self, *args, **kwargs):
        super(Sede, self).save(*args, **kwargs)
        if self.__attiva_default is not None and not self.attiva and self.__attiva_default != self.attiva:
            for sottosede in self.ottieni_figli(solo_attivi=False):
                sottosede.attiva = False
                sottosede.save()

    def sorgente_slug(self):
        if self.estensione == PROVINCIALE:
            suffisso = '-p'
        else:
            suffisso = ''
        if self.genitore:
            return str(self.genitore.slug) + "-" + self.nome + suffisso
        else:
            return self.nome + suffisso

    slug = AutoSlugField(populate_from=sorgente_slug, slugify=sede_slugify, always_update=True, max_length=2000, unique=True)
    membri = models.ManyToManyField(Persona, through='Appartenenza', through_fields=('sede', 'persona'))

    @property
    def url(self):
        if self.estensione == TERRITORIALE:
            return self.comitato.url
        return "/informazioni/sedi/%s/" % self.slug

    @property
    def url_checklist(self):
        return "/presidente/checklist/%d/" % self.pk

    @property
    def ha_checklist(self):
        return self.tipo == self.COMITATO and self.estensione in [NAZIONALE, REGIONALE, PROVINCIALE, LOCALE]

    @property
    def richiede_revisione_dati(self):
        """
        Ritorna True se i dati non sono stati aggiornati dall'entrata in carica del Presidente/Commissario.
        """
        # Deve essere un Comitato
        if not self.comitato == self:
            return False
        delegato_attuale = self.deleghe_attuali(tipo=PRESIDENTE).first()
        # Se non esiste controllo che ci sia un commissario
        if not delegato_attuale:
            delegato_attuale = self.deleghe_attuali(tipo=COMMISSARIO).first()
        # Ricontrollo se non esiste il commissario non è presidiata
        if not delegato_attuale:
            return False
        # Deve avere una locazione geografica
        if not self.locazione:
            return True

        return self.ultima_modifica < delegato_attuale.inizio

    @property
    def link(self):
        return "<a href='%s' target='_new'>%s</a>" % (
            self.url, self.nome_completo
        )

    @property
    def colore_mappa(self):
        dict = {
            NAZIONALE: "green",
            REGIONALE: "green",
            PROVINCIALE: "orange",
            LOCALE: "red",
            TERRITORIALE: "blue",
        }
        return dict[self.estensione]

    # Q: Come ottengo i dati del comitato?
    # A: Usa la funzione Sede.ottieni, ad esempio, Sede.ottieni('partita_iva').
    #    Questa funzione cerca la prima partita IVA disponibile a "Salire" l'albero.

    def ottieni(self, nome_campo):
        """
        Questa funzione dovrebbe essere usata per ottenere i campi di un comitato.
        Se il campo non e' definito, risale l'albero per ottenerlo.
        :param nome_campo: Nome del campo, es. "codice_fiscale", "partita_iva", ecc.
        :return: Il primo valore disponibile o None se non trovato.
        """
        attuale = self
        while True:
            if attuale.__getattribute__(nome_campo):
                return attuale.__getattribute__(nome_campo)
            if attuale.genitore is None:
                return None
            attuale = attuale.genitore

    def appartenenze_attuali(self, membro=None, figli=False, al_giorno=None, **kwargs):
        """
        Ritorna l'elenco di appartenenze attuali ad un determinato giorno.
        Altri parametri (**kwargs) possono essere aggiunti.

        :param membro: Se specificato, filtra per tipologia di membro (es. Appartenenza.VOLONTARIO).
        :param figli: Se vero, ricerca anche tra i comitati figli.
        :param al_giorno: Default oggi. Giorno da controllare.
        :return: Ricerca filtrata per appartenenze attuali.
        """

        # Inizia la ricerca dalla mia discendenza o da me solamente?
        if figli:
            f = Appartenenza.objects.filter(sede__in=self.ottieni_discendenti(True))
        else:
            f = self.appartenenze

        f = f.filter(
            Appartenenza.query_attuale(al_giorno=al_giorno).q,
            **kwargs
        )

        # Se richiesto, filtra per tipo membro (o tipi)
        if membro is not None:
            if is_list(membro):
                f = f.filter(membro__in=membro)
            else:
                f = f.filter(membro=membro)

        # NB: Vengono collegate via Join le tabelle Persona e Sede per maggiore efficienza.
        return f.select_related('persona', 'sede')

    def membri_attuali(self, figli=False, al_giorno=None, **kwargs):
        """
        Ritorna i membri attuali, eventualmente filtrati per tipo, del sede.
        :param figli: Se vero, ricerca anche tra i comitati figli.
        :param al_giorno: Default oggi. Giorno da controllare.
        :param membro: Se filtrare per membro.
        :return:
        """
        if figli:
            kwargs.update({'sede__in': self.ottieni_discendenti(includimi=True)})
        else:
            kwargs.update({'sede': self.pk})

        return Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, **kwargs).via("appartenenze"))\
                .distinct('nome', 'cognome', 'codice_fiscale')

    def appartenenze_persona(self, persona, membro=None, figli=False, **kwargs):
        """
        Ottiene le appartenenze attuali di una data persona, o None se la persona non appartiene al sede.
        """
        self.appartenenze_attuali(membro=membro, figli=figli, persona=persona, **kwargs)

    def ha_membro(self, persona, membro=None, figli=False, **kwargs):
        """
        Controlla se una persona e' membro del sede o meno.
        """
        return self.appartenenze_persona(persona, membro=membro, figli=figli, **kwargs).exists()

    def __str__(self):
        if self.estensione == TERRITORIALE and self.genitore is not None:
            return "%s: %s" % (self.genitore.nome, self.nome,)

        else:
            return "%s" % (self.nome,)

    def presidente(self):
        delega_presidenziale = self.comitato.delegati_attuali(tipo=PRESIDENTE, solo_deleghe_attive=True).first()
        if not delega_presidenziale:
            delega_presidenziale = self.comitato.delegati_attuali(tipo=COMMISSARIO, solo_deleghe_attive=True).first()
        return delega_presidenziale

    def vice_presidente(self):
        delega_vice_presidenziale = self.comitato.delegati_attuali(tipo=VICE_PRESIDENTE, solo_deleghe_attive=True).first()
        return delega_vice_presidenziale if delega_vice_presidenziale else None

    def consigliere_giovane(self):
        delega_consigliere_giovane = self.comitato.delegati_attuali(tipo=CONSIGLIERE_GIOVANE, solo_deleghe_attive=True).first()
        return delega_consigliere_giovane if delega_consigliere_giovane else None

    def consiglieri(self):
        delega_consiglieri = self.comitato.delegati_attuali(tipo=CONSIGLIERE, solo_deleghe_attive=True)
        return delega_consiglieri if delega_consiglieri else []

    def delegati_ufficio_soci(self):
        """
        Ottiene le persone in questo ordine:
        1. Prova con ufficio soci di questa sede; se non esiste
        2. Prova con ufficio soci del comitato di questa sede; se non esiste
        3. Prova com presidente di questa sede; se non esiste
        4. Ritorna un queryset vuoto Persona.
        :return:
        """
        delegati = self.delegati_attuali(tipo__in=[UFFICIO_SOCI, UFFICIO_SOCI_UNITA])
        if not delegati.exists():
            delegati = self.comitato.delegati_attuali(tipo__in=[UFFICIO_SOCI, UFFICIO_SOCI_UNITA])
        if not delegati.exists():
            delegati = self.comitato.delegati_attuali(tipo=PRESIDENTE)
        return delegati

    @property
    def nome_completo(self):
        return str(self)

    def esplora(self, includi_me=True):
        """
        Ritorna un QuerySet di tutte le Sedi sottostanti.
        :param includi_me: Se True, include me stesso.
        :return: QuerySet.
        """
        return self.ottieni_discendenti(includimi=includi_me)

    @property
    def comitato(self):
        """
        Ottiene il comitato a cui afferisce la Sede attuale.
        :return: Oggetto Sede o None.
        """

        # Regionale e Nazionale sono Comitati.
        if self.estensione in [LOCALE, PROVINCIALE, REGIONALE, NAZIONALE]:
            return self

        # Se sono unita' territoriale, ritorna il mio genitore.
        return self.genitore

    def superiore(self, estensione=LOCALE):
        """
        Ritorna la sede superiore con estensione specificata
        :param estensione:
        :return:
        """
        x = self
        while True:
            try:
                x = x.genitore
                if x.estensione == estensione:
                    return x
            except:
                return None

    @property
    def domanda_formativa(self):
        from formazione.models import Aspirante
        return self.circonferenze_contenenti(Aspirante.query_contattabili()).count()

    @property
    def domanda_formativa_raggio_medio(self):
        from formazione.models import Aspirante
        aspiranti = self.circonferenze_contenenti(Aspirante.query_contattabili())
        return int(aspiranti.aggregate(raggio=Avg('raggio'))['raggio']) or 0

    def espandi(self, includi_me=False, pubblici=False, ignora_disattive=True):
        """
        Espande la Sede.
        Se pubblico, me e tutte le sedi sottostanti.
        Se privato, me e le unita' territoriali incluse.
        Se la sede è un territoriale non ha nessun discendete quindi ritorna semplicemente se stesso.
        :param includi_me: Includimi nel queryset ritornato.
        :param pubblici: Espandi i pubblici, ritornando tutto al di sotto.
        :param ignora_disattive: Nasconde le sedi disattive.
        """

        # Sede Territoriale ritorna se stessa
        if self.estensione == TERRITORIALE:
            return self.queryset_modello()

        # Sede pubblica... ritorna tutto sotto di se.
        if pubblici and self.estensione in [NAZIONALE, REGIONALE]:
            queryset = self.ottieni_discendenti(includimi=includi_me)

        # Sede privata... espandi con unita' territoriali.
        elif self.estensione in [PROVINCIALE, LOCALE]:
            queryset = self.ottieni_figli().filter(estensione=TERRITORIALE) | self.queryset_modello()

        # Sede territoriale. Solo me, se richiesto.
        elif includi_me:
            queryset = self.queryset_modello()

        else:
            queryset = self.__class__.objects.none()


        # Cosa fare con le sedi disattive?
        if ignora_disattive:
            return queryset.filter(attiva=True)

        else:
            return queryset

    def comitati_sottostanti(self):
        """
        Ritorna un elenco di Comitati sottostanti.
        Es. Regionale -> QuerySet Provinciali
        """
        return self.ottieni_figli().filter(estensione__in=(REGIONALE, PROVINCIALE, LOCALE))

    def unita_sottostanti(self):
        return self.ottieni_figli().filter(estensione=TERRITORIALE)


class Delega(ModelloSemplice, ConStorico, ConMarcaTemporale):
    """
    Rappresenta una delega ad una funzione.

    Una delega abilita una persona all'accesso ad una determinata funzionalita' -espressa
    dal tipo della delega- su di un determinato elemento -espressa dall'oggetto-.

    Una delega ha inizio e fine. Una fine None-NULL rappresenta una fine indeterminata.
    """

    class Meta:
        verbose_name_plural = "Deleghe"
        app_label = 'anagrafica'
        index_together = [
            ['oggetto_tipo', 'oggetto_id'],
            ['tipo', 'oggetto_tipo', 'oggetto_id'],
            ['persona', 'tipo'],
            ['persona', 'tipo', 'stato'],
            ['persona', 'stato'],
            ['inizio', 'fine'],
            ['inizio', 'fine', 'stato'],
            ['persona', 'inizio', 'fine', 'tipo',],
            ['persona', 'inizio', 'fine', 'tipo', 'stato'],
            ['persona', 'inizio', 'fine',],
            ['persona', 'inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo',],
            ['inizio', 'fine', 'tipo',],
            ['inizio', 'fine', 'tipo', 'oggetto_id', 'oggetto_tipo'],
        ]
        permissions = (
            ("view_delega", "Can view delega"),
        )

    ATTIVA = "a"
    SOSPESA = "s"
    STATO = ((ATTIVA, "Attiva"),
             (SOSPESA, "Sospesa"))

    persona = models.ForeignKey(Persona, db_index=True, related_name='deleghe', related_query_name='delega', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=2, db_index=True, choices=PERMESSI_NOMI)
    stato = models.CharField(max_length=2, db_index=True, choices=STATO, default=ATTIVA)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True, on_delete=models.SET_NULL, null=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')
    firmatario = models.ForeignKey(Persona, db_index=True, null=True, default=None, related_name='deleghe_firmate',
                                   related_query_name='delega_firmata', on_delete=models.SET_NULL)

    def __str__(self):
        return "Delega %s di %s come %s per %s" % (
            "attuale" if self.attuale() else "passata",
            self.persona.codice_fiscale,
            self.get_tipo_display(), self.oggetto,
        )

    def permessi(self, solo_deleghe_attive=True):
        """
        Ottiene un elenco di permessi che scaturiscono dalla delega.
        :param solo_deleghe_attive: Espandi permessi solo dalle deleghe attive.
        :return: Una lista di permessi.
        """
        return delega_permessi(self, solo_deleghe_attive=solo_deleghe_attive)

    def espandi_incarichi(self):
        """
        Ottiene un elenco di incarichi che scaturiscono dalla delega.
        :return: Una lista di tuple (INCARICO, qs_oggetto)
        """
        return delega_incarichi(self)

    def autorizzazioni(self):  # TODO Rimuovere
        """
        Ottiene le autorizzazioni firmabili da questo ruolo.
        :return: QuerySet
        """
        oggetto_tipo = ContentType.objects.get_for_model(self.oggetto)
        return Autorizzazione.objects.filter(destinatario_ruolo=self.tipo,
                                             destinatario_oggetto_tipo__pk=oggetto_tipo.pk,
                                             destinatario_oggetto_id=self.oggetto.pk)

    def invia_notifica_creazione(self):
        messaggi = []
        messaggi += [Messaggio.costruisci_e_invia(
            oggetto="%s per %s" % (self.get_tipo_display(), self.oggetto,),
            modello="email_delega_notifica_creazione.html",
            corpo={
                "delega": self,
            },
            mittente=self.firmatario,
            destinatari=[self.persona],
        )]

        # Se presidente, invia check-list.
        if self.tipo == PRESIDENTE or self.tipo == COMMISSARIO:
            messaggi += [
                 Messaggio.costruisci_e_invia(
                     oggetto="IMPORTANTE: Check-list nuovo {}".format('Presidente' if self.tipo == PRESIDENTE else 'Commissario'),
                     modello="email_delega_notifica_nuova_nomina_presidenziale.html",
                     corpo={
                         "delega": self,
                     },
                     mittente=self.firmatario,
                     destinatari=[self.persona],
                 )
            ]

        return messaggi

    def invia_notifica_terminazione(self, mittente=None, accoda=False):
        if mittente is None:
            mittente = self.firmatario

        funzione = Messaggio.costruisci_e_invia
        if accoda:
            funzione = Messaggio.costruisci_e_accoda

        return funzione(
            oggetto="TERMINATO: %s per %s" % (self.get_tipo_display(), self.oggetto,),
            modello="email_delega_notifica_terminazione.html",
            corpo={
                "delega": self,
                "mittente": mittente,
            },
            mittente=mittente,
            destinatari=[self.persona],
        )

    def termina(self, mittente=None, accoda=False, notifica=True, data=None, *args, **kwargs):
        if kwargs.get('termina_at'):
            """ May be called from: anagrafica.viste.strumenti_delegati_termina
            on the following pages:
            - /presidente/sedi/<id>/delegati/US/
            - /attivita/scheda/<id>/referenti/
            """
            self.fine = kwargs.get('termina_at')
        else:
            self.fine = mezzanotte_24(data)
        self.save()

        if notifica:
            self.invia_notifica_terminazione(mittente=mittente, accoda=accoda)

    def presidenziali_termina_deleghe_dipendenti(self, mittente=None):
        """
        Nel caso di una delega come Presidente o Commissario, termina anche
         tutte le deleghe che dipendono da questa.
        """

        if not self.tipo == PRESIDENTE and not self.tipo == COMMISSARIO:
            raise ValueError("La delega non è di tipo Presidente/Commissario.")

        if self.fine:
            nel_periodo_presidenziale = {
                "inizio__gte": self.inizio,
                "inizio__lte": self.fine,
            }
        else:
            nel_periodo_presidenziale = {
                "inizio__gte": self.inizio
            }

        sede = self.oggetto
        sede_espansa = sede.espandi(includi_me=True)

        from formazione.models import CorsoBase
        from attivita.models import Attivita, Area

        deleghe = Delega.objects.none()
        per_la_sede_espansa = {
            "oggetto_tipo": ContentType.objects.get_for_model(sede),
            "oggetto_id__in": sede_espansa.values_list('id', flat=True),
        }

        deleghe |= Delega.query_attuale(
            tipo__in=[UFFICIO_SOCI, UFFICIO_SOCI_UNITA, DELEGATO_OBIETTIVO_1,
                      DELEGATO_OBIETTIVO_2, DELEGATO_OBIETTIVO_3, DELEGATO_OBIETTIVO_4,
                      DELEGATO_OBIETTIVO_5, DELEGATO_OBIETTIVO_6, RESPONSABILE_FORMAZIONE,
                      RESPONSABILE_AUTOPARCO, DELEGATO_CO, CONSIGLIERE, CONSIGLIERE_GIOVANE, VICE_PRESIDENTE],
        ).filter(**per_la_sede_espansa).filter(**nel_periodo_presidenziale)

        per_i_corsi_delle_sedi = {
            "oggetto_tipo": ContentType.objects.get_for_model(CorsoBase),
            "oggetto_id__in": CorsoBase.objects.filter(sede__in=sede_espansa).values_list('id', flat=True),
        }

        deleghe |= Delega.query_attuale(
            tipo=DIRETTORE_CORSO,
        ).filter(**per_i_corsi_delle_sedi).filter(**nel_periodo_presidenziale)

        per_le_aree_delle_sedi = {
            "oggetto_tipo": ContentType.objects.get_for_model(Area),
            "oggetto_id__in": Area.objects.filter(sede__in=sede_espansa).values_list('id', flat=True)
        }

        deleghe |= Delega.query_attuale(
            tipo=RESPONSABILE_AREA,
        ).filter(**per_le_aree_delle_sedi).filter(**nel_periodo_presidenziale)

        per_le_attivita_delle_sedi = {
            "oggetto_tipo": ContentType.objects.get_for_model(Attivita),
            "oggetto_id__in": Attivita.objects.filter(sede__in=sede_espansa).values_list('id', flat=True)
        }

        deleghe |= Delega.query_attuale(
            tipo=REFERENTE,
        ).filter(**per_le_attivita_delle_sedi).filter(**nel_periodo_presidenziale)

        # Ora, termina tutte queste deleghe.

        numero_deleghe = deleghe.count()

        for delega in deleghe:
            delega.termina(mittente=mittente, accoda=True, termina_at=datetime.now())

        return numero_deleghe


class Fototessera(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):
    """
    Rappresenta una fototessera per la persona.
    """

    class Meta:
        verbose_name_plural = "Fototessere"
        permissions = (
            ("view_fototessera", "Can view fototessera"),
        )

    persona = models.ForeignKey(Persona, related_name="fototessere", db_index=True, on_delete=models.CASCADE)
    file = models.ImageField("Fototessera", upload_to=GeneratoreNomeFile('fototessere/'),
                             validators=[valida_dimensione_file_8mb])

    RICHIESTA_NOME = "Fototessera"


class Trasferimento(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni, ConPDF):
    """
    Rappresenta una pratica di trasferimento.
    """

    class Meta:
        verbose_name = "Richiesta di trasferimento"
        verbose_name_plural = "Richieste di trasferimento"
        permissions = (
            ("view_trasferimento", "Can view Richiesta di trasferimento"),
        )

    richiedente = models.ForeignKey(Persona, related_name='trasferimenti_richiesti_da', on_delete=models.SET_NULL, null=True)
    persona = models.ForeignKey(Persona, related_name='trasferimenti', on_delete=models.CASCADE)
    destinazione = models.ForeignKey(
        Sede, related_name='trasferimenti_destinazione', on_delete=models.PROTECT,
        limit_choices_to={'estensione__in': (PROVINCIALE, LOCALE, TERRITORIALE)}
    )
    appartenenza = models.ForeignKey(Appartenenza, related_name='trasferimento', null=True, blank=True, on_delete=models.PROTECT)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=16, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=2048, null=True, blank=False,)
    massivo = models.BooleanField(null=False, blank=False, default=False,
                                  help_text='Se effettuato tramite spostamento massivo da interfaccia admin')

    RICHIESTA_NOME = "trasferimento"

    # Data fissa di 30gg come da regolamento CRI
    APPROVAZIONE_AUTOMATICA = timedelta(days=30)

    def __str__(self):
        return 'Trasferimento'

    def autorizzazione_concedi_modulo(self):
        from anagrafica.forms import ModuloConsentiTrasferimento
        return ModuloConsentiTrasferimento

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        data = mezzanotte_00(data)
        if auto:
            self.protocollo_data = timezone.now()
            self.protocollo_numero = Autorizzazione.PROTOCOLLO_AUTO
        else:
            self.protocollo_data = modulo.cleaned_data['protocollo_data']
            self.protocollo_numero = modulo.cleaned_data['protocollo_numero']
        self.save()
        self.esegui(auto=auto, notifiche_attive=notifiche_attive, data=data)

    def esegui(self, auto=False, notifiche_attive=True, data=None):
        with atomic():
            appartenenzaVecchia = Appartenenza.objects.filter(
                Appartenenza.query_attuale().q, membro=Appartenenza.VOLONTARIO, persona=self.persona
            ).first()
            appartenenzaVecchia.fine = mezzanotte_24_ieri(data)
            appartenenzaVecchia.terminazione = Appartenenza.TRASFERIMENTO
            appartenenzaVecchia.save()

            da_dipendente = False
            if self.persona.appartenenze_attuali(membro__in=(Appartenenza.DIPENDENTE,)).exists():
                    da_dipendente = True

            self.persona.chiudi_tutto(mezzanotte_24_ieri(data), da_dipendente=da_dipendente)

            # Invia notifica tramite e-mail
            app = Appartenenza.objects.create(
                membro=Appartenenza.VOLONTARIO,
                persona=self.persona,
                sede=self.destinazione,
                inizio=mezzanotte_00(data),
                precedente=appartenenzaVecchia
            )
            self.appartenenza = app
            testo_extra = ''
            if auto:
                self.automatica = True
                testo_extra = 'Il trasferimento è stato automaticamente approvato essendo decorsi trenta giorni, ' \
                              'ai sensi dell\'articolo 9.5 del "Regolamento sull\'organizzazione, le attività, ' \
                              'la formazione e l\'ordinamento dei volontari"'
            else:
                self.automatica = False
            self.save()
            # self.richiedi()
            if notifiche_attive:
                autorizzazione = self.autorizzazioni.first()
                autorizzazione.notifica_sede_autorizzazione_concessa(appartenenzaVecchia.sede, testo_extra)
                autorizzazione.notifica_sede_autorizzazione_concessa(app.sede, testo_extra)

    def richiedi(self, notifiche_attive=True):

        app_trasferibile = self.persona.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        if not app_trasferibile:
            raise ValueError("Impossibile richiedere estensione: Nessuna appartenenza attuale.")
        sede = app_trasferibile.sede

        self.autorizzazione_richiedi_sede_riferimento(
            self.persona,
            INCARICO_GESTIONE_TRASFERIMENTI,
            invia_notifica_presidente=notifiche_attive,
            auto=Autorizzazione.AP_AUTO,
            scadenza=self.APPROVAZIONE_AUTOMATICA,
            forza_sede_riferimento=sede,
        )

    def url(self):
        return "#"

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
          nome="Trasferimento %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "trasferimento": self,
            "sede_attuale": self.persona.sede_riferimento(),
          },
          modello="pdf_trasferimento.html",
        )
        return pdf


class Estensione(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni, ConPDF):
    """
    Rappresenta una pratica di estensione.
    """

    class Meta:
        verbose_name = "Richiesta di estensione"
        verbose_name_plural = "Richieste di estensione"
        permissions = (
            ("view_estensions", "Can view Richiesta di estensione"),
        )

    richiedente = models.ForeignKey(Persona, related_name='estensioni_richieste_da', on_delete=models.SET_NULL, null=True)
    persona = models.ForeignKey(Persona, related_name='estensioni', on_delete=models.CASCADE)
    destinazione = models.ForeignKey(
        Sede, related_name='estensioni_destinazione', on_delete=models.PROTECT,
        limit_choices_to={'estensione__in': (PROVINCIALE, LOCALE, TERRITORIALE)}
    )
    appartenenza = models.ForeignKey(Appartenenza, related_name='estensione', null=True, blank=True, on_delete=models.CASCADE)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=512, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=4096, null=True, blank=False,)

    RICHIESTA_NOME = "Estensione"

    def attuale(self, **kwargs):
        """ Controlla che l'estensione sia stata confermata
        e l'appartenenza creata sia in corso. """
        app_attuale = self.appartenenza
        app_attuale = False if app_attuale is None \
                            else app_attuale.attuale(**kwargs)
        return self.esito == self.ESITO_OK and app_attuale

    def autorizzazione_concedi_modulo(self):
        from anagrafica.forms import ModuloConsentiEstensione
        return ModuloConsentiEstensione

    def autorizzazione_nega_modulo(self):
        from anagrafica.forms import ModuloNegaEstensione
        return ModuloNegaEstensione

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        if data is None or not isinstance(data, date):
            data = poco_fa()
        data = datetime(data.year, data.month, data.day)
        self.protocollo_data = modulo.cleaned_data['protocollo_data'] if modulo else None
        self.protocollo_numero = modulo.cleaned_data['protocollo_numero'] if modulo else None
        origine = self.persona.sede_riferimento()
        app = Appartenenza(
            membro=Appartenenza.ESTESO,
            persona=self.persona,
            sede=self.destinazione,
            inizio=data,
            fine=data + timedelta(days=365)
        )
        app.save()
        self.appartenenza = app
        self.save()
        testo_extra = ''
        self.autorizzazioni.first().notifica_sede_autorizzazione_concessa(origine, testo_extra)
        self.autorizzazioni.first().notifica_sede_autorizzazione_concessa(app.sede, testo_extra)

    def richiedi(self, notifiche_attive=True):
        app_estendibile = self.persona.appartenenze_attuali(membro=Appartenenza.VOLONTARIO).first()
        if not app_estendibile:
            raise ValueError("Impossibile richiedere estensione: Nessuna appartenenza attuale.")
        sede = app_estendibile.sede
        self.autorizzazione_richiedi_sede_riferimento(
            self.persona,
            INCARICO_GESTIONE_ESTENSIONI,
            invia_notifica_presidente=notifiche_attive,
            auto=Autorizzazione.MANUALE,
            forza_sede_riferimento=sede,
        )
        if self.destinazione.presidente():
            Messaggio.costruisci_e_invia(
               oggetto="Notifica di Estensione in entrata",
               modello="email_richiesta_estensione_cc.html",
               corpo={
                   "estensione": self,
               },
               mittente=None,
               destinatari=[
                    self.destinazione.presidente(),
               ]
            )

    def termina(self, data=None):
        self.appartenenza.fine = mezzanotte_24(data)
        self.appartenenza.terminazione = Appartenenza.FINE_ESTENSIONE
        self.appartenenza.save()

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        appartenenza = Appartenenza.objects.filter(Appartenenza.query_attuale(al_giorno=self.creazione).q,
                                                   membro=Appartenenza.VOLONTARIO, persona=self.persona).first()
        pdf.genera_e_salva(
          nome="Estensione %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "estensione": self,
            "sede_attuale": self.persona.sede_riferimento(),
            "appartenenza": appartenenza,
          },
          modello="pdf_estensione.html",
        )
        return pdf


class Riserva(ModelloSemplice, ConMarcaTemporale, ConStorico, ConProtocollo,
              ConAutorizzazioni, ConPDF):
    """
    Rappresenta una pratica di riserva.
    Questa puo' essere in corso o meno.
    """

    class Meta:
        verbose_name = "Richiesta di riserva"
        verbose_name_plural = "Richieste di riserva"
        index_together = [
            ['inizio', 'fine'],
            ['persona', 'inizio', 'fine'],
        ]
        permissions = (
            ("view_riserva", "Can view Richiesta di riserva"),
        )

    RICHIESTA_NOME = "riserva"
    persona = models.ForeignKey(Persona, related_name="riserve", on_delete=models.CASCADE)
    motivo = models.CharField(max_length=4096)
    appartenenza = models.ForeignKey(Appartenenza, related_name="riserve", on_delete=models.PROTECT)

    def richiedi(self, notifiche_attive=True):
        self.autorizzazione_richiedi_sede_riferimento(
            self.persona,
            INCARICO_GESTIONE_RISERVE,
            invia_notifica_presidente=notifiche_attive
        )
        if notifiche_attive:
            self.invia_mail()

    def autorizzazione_concedi_modulo(self):
        from anagrafica.forms import ModuloConsentiRiserva
        return ModuloConsentiRiserva

    def autorizzazione_concessa(self, modulo=None, auto=False, notifiche_attive=True, data=None):
        if auto:
            self.protocollo_data = timezone.now()
            self.protocollo_numero = 'AUTO'
        else:
            self.protocollo_data = modulo.cleaned_data['protocollo_data']
            self.protocollo_numero = modulo.cleaned_data['protocollo_numero']
        self.save()
        testo_extra = ''
        self.autorizzazioni.first().notifica_sede_autorizzazione_concessa(self.persona.sede_riferimento(), testo_extra)

    def termina(self, data=None):
        self.fine = mezzanotte_24(data)
        self.save()

    def invia_mail(self):

        Messaggio.costruisci_e_invia(
           oggetto="Richiesta di riserva",
           modello="email_richiesta_riserva.html",
           corpo={
               "riserva": self,
           },
           mittente=None,
           destinatari=[
                self.persona,
           ]
        )

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
          nome="Riserva %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "riserva": self,
            "sede_attuale": self.persona.sede_riferimento()
          },
          modello="pdf_riserva.html",
        )
        return pdf


class ProvvedimentoDisciplinare(ModelloSemplice, ConMarcaTemporale, ConProtocollo, ConStorico):
    AMMONIZIONE = "A"
    SOSPENSIONE = "S"
    ESPULSIONE = "E"
    TIPO = (
        (AMMONIZIONE, "Ammonizione",),
        (SOSPENSIONE, "Sospensione",),
        (ESPULSIONE, "Esplusione",),
    )

    persona = models.ForeignKey(Persona, related_name="provvedimenti", on_delete=models.CASCADE)
    registrato_da = models.ForeignKey(Persona, related_name="provvedimenti_registrati", on_delete=models.SET_NULL, null=True)
    sede = models.ForeignKey(Sede, related_name="provvedimenti", on_delete=models.PROTECT)
    motivazione = models.CharField(max_length=500)
    tipo = models.CharField(max_length=1, choices=TIPO, default=AMMONIZIONE)

    def esegui(self):

        Messaggio.costruisci_e_invia(
            oggetto="Provvedimento Disciplinare: %s" % (self.get_tipo_display(),),
            modello="email_provvedimento.html",
            corpo={
                "provvedimento": self,
            },
            mittente=self.registrato_da, destinatari=[
                self.persona
            ]
        )

        if self.tipo == self.ESPULSIONE:
            self.persona.espelli()

    class Meta:
        verbose_name = "Provvedimento Disciplinare"
        verbose_name_plural = "Provvedimenti Disciplinari"
        permissions = (
            ('view_provvedimentodisciplinare', "Can view Provvediemto disciplinare"),
        )
    
    def __str__(self):
        return self.persona.__str__()


class Dimissione(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Documento di Dimissione"
        verbose_name_plural = "Documenti di Dimissione"
        permissions = (
            ("view_dimissione", "Can view Documento di Dimissione"),
        )

    persona = models.ForeignKey(Persona, related_name="dimissioni", on_delete=models.CASCADE)
    appartenenza = models.ForeignKey(Appartenenza, related_name="dimissioni", on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, related_name="dimissioni", on_delete=models.PROTECT)

    VOLONTARIE = 'VOL'
    TURNO = 'TUR'
    RISERVA = 'RIS'
    QUOTA = 'QUO'
    RADIAZIONE = 'RAD'
    DECEDUTO = 'DEC'
    TRASFORMAZIONE = 'TRA'
    SCADENZA = 'SCA'
    ALTRO = 'ALT'

    MOTIVI_VOLONTARI = (
        (VOLONTARIE, 'Dimissioni Volontarie'),
        (TURNO, 'Mancato svolgimento turno'),
        (RISERVA, 'Mancato rientro da riserva'),
        (QUOTA, 'Mancato versamento quota annuale'),
        (RADIAZIONE, 'Radiazione da Croce Rossa Italiana'),
        (SCADENZA, 'Scadenza contratto o altro'),
        (DECEDUTO, 'Decesso'),
    )

    MOTIVI_ALTRI = (
        (TRASFORMAZIONE, 'Trasformazione in volontario'),
        (ALTRO, 'Altro'),
    )

    MOTIVI = MOTIVI_VOLONTARI + MOTIVI_ALTRI

    motivo = models.CharField(choices=MOTIVI, max_length=3)
    info = models.CharField(max_length=512, help_text="Maggiori informazioni sulla causa della dimissione")
    richiedente = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True)

    def applica(self, applicante=None, trasforma_in_sostenitore=False, invia_notifica=True):
        from gruppi.models import Appartenenza as App
        precedente_appartenenza = self.appartenenza
        precedente_sede = precedente_appartenenza.sede
        destinatari = set()
        presidente = None
        if precedente_sede:
            us = precedente_sede.delegati_ufficio_soci()
            destinatari = set(us)
            presidente = precedente_sede.presidente()
            destinatari.add(presidente)

        if precedente_appartenenza.membro == Appartenenza.SOSTENITORE:
            template = "email_dimissioni_sostenitore.html"
        else:
            template = "email_dimissioni.html"

        da_dipendente = False
        if precedente_appartenenza.membro == Appartenenza.DIPENDENTE:
            if self.persona.appartenenze_attuali(membro__in=(Appartenenza.VOLONTARIO, Appartenenza.SOSTENITORE)).exists():
                da_dipendente = True

        # impostiamo l'orario di chiusura alle 0.0 del giorno corrente
        data = poco_fa()
        if precedente_appartenenza.membro == Appartenenza.VOLONTARIO:
            # Delega.query_attuale(al_giorno=self.creazione, persona=self.persona).update(fine=mezzanotte_24_ieri(data))
            App.query_attuale(al_giorno=self.creazione, persona=self.persona).update(fine=mezzanotte_24_ieri(data))
            #TODO reperibilita'
            [
                [x.autorizzazioni_ritira() for x in y.con_esito_pending().filter(persona=self.persona)]
                for y in [Estensione, Trasferimento, Partecipazione, TitoloPersonale]
            ]
        Appartenenza.query_attuale(
            al_giorno=self.creazione, persona=self.persona, membro=precedente_appartenenza.membro
        ).update(fine=mezzanotte_24_ieri(data), terminazione=Appartenenza.DIMISSIONE)

        self.persona.chiudi_tutto(mezzanotte_24_ieri(data), mittente_mail=applicante, da_dipendente=da_dipendente)

        if trasforma_in_sostenitore:
            app = Appartenenza(precedente=precedente_appartenenza, persona=self.persona,
                               sede=precedente_sede,
                               inizio=mezzanotte_00(data),
                               membro=Appartenenza.SOSTENITORE)
            app.save()

        if invia_notifica:

            if self.motivo == self.DECEDUTO:

                for destinatario in destinatari:
                    Messaggio.costruisci_e_invia(
                        oggetto="Dimissioni per decesso",
                        modello="email_dimissioni_decesso.html",
                        corpo={
                            "dimissione": self,
                            "destinatario": destinatario,
                            "carica": "Presidente" if destinatario == presidente else "Delegato Ufficio Soci"
                        },
                        mittente=self.richiedente,
                        destinatari=[destinatario]
                    )

            else:

                Messaggio.costruisci_e_invia(
                    oggetto="Dimissioni",
                    modello=template,
                    corpo={
                        "dimissione": self,
                    },
                    mittente=self.richiedente,

                    destinatari=[
                        self.persona
                    ]
                )

