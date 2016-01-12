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

import codicefiscale
import mptt
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q, QuerySet
from django_countries.fields import CountryField
import phonenumbers
from model_utils.managers import PassThroughManagerMixin

from anagrafica.costanti import ESTENSIONE, TERRITORIALE, LOCALE, PROVINCIALE, REGIONALE, NAZIONALE

from anagrafica.permessi.applicazioni import PRESIDENTE, PERMESSI_NOMI, APPLICAZIONI_SLUG_DICT, PERMESSI_NOMI_DICT
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.costanti import GESTIONE_ATTIVITA, PERMESSI_OGGETTI_DICT, GESTIONE_SOCI, GESTIONE_CORSI_SEDE, GESTIONE_CORSO, \
    GESTIONE_SEDE, GESTIONE_AUTOPARCHI_SEDE
from anagrafica.permessi.delega import delega_permessi
from anagrafica.permessi.persona import persona_ha_permesso, persona_oggetti_permesso, persona_permessi, \
    persona_permessi_almeno, persona_ha_permessi
from anagrafica.validators import valida_codice_fiscale, ottieni_genere_da_codice_fiscale, \
    crea_validatore_dimensione_file, valida_dimensione_file_8mb, valida_dimensione_file_5mb, valida_almeno_14_anni
from attivita.models import Turno
from base.files import PDF
from base.geo import ConGeolocalizzazioneRaggio, ConGeolocalizzazione
from base.models import ModelloSemplice, ModelloCancellabile, ModelloAlbero, ConAutorizzazioni, ConAllegati, \
    Autorizzazione, ConVecchioID
from base.stringhe import normalizza_nome, GeneratoreNomeFile
from base.tratti import ConMarcaTemporale, ConStorico, ConProtocollo, ConDelegati, ConPDF
from base.utils import is_list, sede_slugify
from autoslug import AutoSlugField

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

    # Informazioni anagrafiche
    nome = models.CharField("Nome", max_length=64)
    cognome = models.CharField("Cognome", max_length=64)
    codice_fiscale = models.CharField("Codice Fiscale", max_length=16, blank=False,
                                      unique=True, db_index=True, validators=[valida_codice_fiscale,])
    data_nascita = models.DateField("Data di nascita", db_index=True, null=True,
                                    validators=[valida_almeno_14_anni])
    genere = models.CharField("Genere", max_length=1, choices=GENERE, db_index=True)

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
    email_contatto = models.EmailField("Email di contatto", max_length=64, blank=True)
    note = models.TextField("Note aggiuntive", max_length=10000, blank=True, null=True,)

    avatar = models.ImageField("Avatar", blank=True, null=True,
                               upload_to=GeneratoreNomeFile('avatar/'),
                               validators=[valida_dimensione_file_5mb])

    @property
    def nome_completo(self):
        """
        Restituisce il nome e cognome
        :return: "Nome Cognome".
        """
        return normalizza_nome(self.nome + " " + self.cognome)

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
        return ottieni_genere_da_codice_fiscale(self.codice_fiscale, default=None)

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

    def __str__(self):
        return self.nome_completo

    class Meta:
        verbose_name_plural = "Persone"
        app_label = 'anagrafica'

    # Q: Qual e' il numero di telefono di questa persona?
    # A: Una persona puo' avere da zero ad illimitati numeri di telefono.
    #    - Persona.numeri_telefono ottiene l'elenco di oggetti Telefono.
    #    - Per avere un elenco di numeri di telefono formattati, usare ad esempio
    #       numeri = [str(x) for x in Persona.numeri_telefono]
    #    - Usare Persona.aggiungi_numero_telefono per aggiungere un numero di telefono.

    def deleghe_attuali(self, al_giorno=date.today(), **kwargs):
        """
        Ritorna una ricerca per le deleghe che son attuali.
        """
        return self.deleghe.filter(Delega.query_attuale(al_giorno).q, **kwargs)

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
    def eta(self, al_giorno=date.today()):
        """
        Ottiene l'eta' in anni del volontario.
        """

        return al_giorno.year - self.data_nascita.year - ((al_giorno.month, al_giorno.day) < (self.data_nascita.month, self.data_nascita.day))

    @property
    def giovane(self, **kwargs):
        return self.eta <= self.ETA_GIOVANE

    """
    # Gestione della Privacy

    * Ottenere il livello di Privacy su di un elemento
      `p.policy(CELLULARE) => Privacy.POLICY_SEDE`

    * Imposta il livello di Privacy su di un elemento
      `p.policy(CELLULARE, Privacy.POLICY_PUBBLICO)`

    * Ottenere una informazione su una Persona "p", solo
      se ho la Policy minima indicata.
      `p.ottieni(Privacy.POLICY_SEDE, CELLULARE)
        > "numero di cellulare", oppure None
    """
    def policy(self, campo, nuova_policy=None):
        """
        Ottiene o cambia la Privacy policy per un campo.
         * Ottenere: `p.policy(CELLULARE) => Privacy.POLICY_SEDE`
         * Cambiare: `p.policy(CELLULARE, Privacy.POLICY_PUBBLICO)`
        """

        if nuova_policy:  # Se sto impostando nuova policy

            try:  # Prova a modificare
                p = Privacy.objects.get(persona=self, campo=campo)
                p.policy = nuova_policy
                p.save()

            except ObjectDoesNotExist:  # Altrimenti crea policy
                p = Privacy(
                    persona=self,
                    campo=campo,
                    policy=nuova_policy
                )
                p.save()

            return

        # Se sto invece ottenendo
        try:
            p = Privacy.objects.get(persona=self, campo=campo)
            return p.policy

        except ObjectDoesNotExist:  # Policy di default
            return Privacy.POLICY_DEFAULT

    def ottieni(self, policy_minima, campo):
        """
        Ottiene il campo se e solo se la policy minima e' soddisfatta.
        Altrimenti ritorna None.
        """
        policy = self.policy(campo)

        if policy >= policy_minima:

            if campo not in Privacy.CAMPO_OTTIENI_DICT:
                raise ValueError("Campo %s non specificato nelle Privacy Policy." % (campo,))

            return Privacy.CAMPO_OTTIENI_DICT[campo](self)

        return None

    def ultimo_accesso_testo(self):
        """
        Ottiene l'ultimo accesso in testo, senza ledere la privacy.
        """
        if not self.utenza or not self.utenza.ultimo_accesso:
            return "Mai"

        if self.utenza.ultimo_accesso > date.today().timedelta(days=-5):
            return "Recentemente"

        if self.utenza.ultimo_accesso > date.today().timedelta(months=-1):
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
    def donatore(self, **kwargs):
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
    def applicazioni_disponibili(self):
        lista = []

        if self.volontario:
            lista += [('/utente/', 'Volontario', 'fa-user')]

        else:
            lista += [('/utente/', 'Utente', 'fa-user')]

        if hasattr(self, 'aspirante'):
            lista += [('/aspirante/', 'Aspirante', 'fa-user', self.aspirante.corsi().count())]

        lista += [('/attivita/', 'Attività', 'fa-calendar')]
        lista += [('/posta/', 'Posta', 'fa-envelope')]

        if self.ha_pannello_autorizzazioni:
            lista += [('/autorizzazioni/', 'Richieste', 'fa-user-plus', self.autorizzazioni_in_attesa().count())]

        if self.ha_permesso(GESTIONE_SEDE):
            lista += [('/presidente/', 'Sedi CRI', 'fa-home')]

        if self.ha_permesso(GESTIONE_SOCI):
            lista += [('/us/', 'Soci', 'fa-users')]

        if self.ha_permesso(GESTIONE_AUTOPARCHI_SEDE):
            lista += [('/veicoli/', "Veicoli", "fa-car")]

        if self.ha_permesso(GESTIONE_CORSO) or self.ha_permesso(GESTIONE_CORSI_SEDE):
            lista += [('/formazione/', 'Formazione', 'fa-graduation-cap')]

        tipi = []
        for d in self.deleghe_attuali():
            if d.tipo in tipi:
                continue
            tipi.append(d.tipo)
            #lista += [(APPLICAZIONI_SLUG_DICT[d.tipo], PERMESSI_NOMI_DICT[d.tipo])]

        return lista


    def oggetti_permesso(self, permesso, al_giorno=date.today()):
        """
        Dato un permesso, ritorna un queryset agli oggetti che sono coperti direttamente
        dal permesso. Es.: GESTIONE_SOCI -> Elenco dei Comitati in cui si ha gestione dei soci.
        :param permesso: Permesso singolo.
        :param al_giorno: Data di verifica.
        :return: QuerySet. Se permesso non valido, QuerySet vuoto o None (EmptyQuerySet).
        """
        permessi = persona_oggetti_permesso(self, permesso, al_giorno=al_giorno)
        if isinstance(permessi, QuerySet):
            return permessi
        else:
            return apps.get_model(PERMESSI_OGGETTI_DICT[permesso][0], PERMESSI_OGGETTI_DICT[permesso][1]).objects.none()

    def permessi(self, oggetto, al_giorno=date.today()):
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

    def permessi_almeno(self, oggetto, minimo, al_giorno=date.today()):
        """
        Controlla se ho i permessi minimi richiesti specificati su un dato oggetto.

        :param oggetto: Oggetto qualunque.
        :param minimo: Oggetto qualunque.
        :param al_giorno:  Data di verifica.
        :return: True se permessi >= minimo, False altrimenti
        """
        return persona_permessi_almeno(self, oggetto, minimo=minimo, al_giorno=al_giorno)

    def ha_permesso(self, permesso, al_giorno=date.today()):
        """
        Dato un permesso, ritorna true se il permesso e' posseduto.
        :param permesso: Permesso singolo.
        :param al_giorno: Data di verifica.
        :return: True se il permesso e' posseduto. False altrimenti.
        """
        return persona_ha_permesso(self, permesso, al_giorno=al_giorno)

    def ha_permessi(self, *permessi):
        """
        Dato un elenco di permessi, ritorna True se tutti i permessi sono posseduti.
        :param permessi: Elenco di permessi.
        :return: True se tutti i permessi sono posseduti. False altrimenti.
        """
        return persona_ha_permessi(self, *permessi)

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
    def url_profilo_credenziali(self):
        return "%scredenziali/" % (self.url,)

    @property
    def url_profilo_appartenenze(self):
        return "%sappartenenze/" % (self.url,)

    @property
    def url_profilo_deleghe(self):
        return "%sdeleghe/" % (self.url,)

    @property
    def url_profilo_appartenenze(self):
        return "%sdeleghe/" % (self.url,)

    @property
    def url_profilo_(self):
        return "%sappartenenze/" % (self.url,)


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
        sedi = self.sedi_attuali(membro__in=Appartenenza.MEMBRO_ATTIVITA)
        return Turno.objects.filter(
            # Attivita visibile


            # Attivtia organizzate dai miei comitati
            Q(attivita__sede__in=sedi)
            # Attivita aperte ai miei comitati
            | Q(attivita__estensione__in=Sede.objects.get_queryset_ancestors(sedi, include_self=True))

            # Attivita che gesticsco
            | Q(attivita__in=self.oggetti_permesso(GESTIONE_ATTIVITA))
            , inizio__gte=inizio, fine__lt=(fine + timedelta(1))
        ).order_by('inizio')

    @property
    def ha_pannello_autorizzazioni(self):
        """
        Ritorna True se il pannello autorizzazioni deve essere mostrato per l'utente.
        False altrimenti.
        """
        return self.deleghe_attuali().exists() or self.autorizzazioni_in_attesa().exists()

    def autorizzazioni(self):
        """
        Ritorna tutte le autorizzazioni firmabili da questo utente.
        :return: QuerySet<Autorizzazione>.
        """
        r = Autorizzazione.objects.none()
        for delega in self.deleghe_attuali():
            r |= delega.autorizzazioni()
        return r

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

    def deleghe_anagrafica(self):
        """
        Ritora un queryset di tutte le deleghe attuali alle persone che sono
        autorizzate a gestire la scheda anagrafica di questa persona.
        :return: QuerySet<Delega>
        """
        i = Delega.objects.none()
        for s in self.sedi_attuali(membro__in=Appartenenza.MEMBRO_DIRETTO):
            i |= s.deleghe_attuali().filter(tipo__in=[PRESIDENTE, UFFICIO_SOCI])
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
            Q(pk__in=Estensione.con_esito_ok())
        )

    def estensioni_in_attesa(self):
        return self.estensioni.all().filter(
            Q(pk__in=Estensione.con_esito_pending())
        )

    def estensioni_attuali_e_in_attesa(self):
        return self.estensioni_attuali() | self.estensioni_in_attesa()


    def espelli(self):
        for appartenenza in self.appartenenze_attuali():
            appartenenza.terminazione = "E"
            appartenenza.fine = datetime.today()

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

    def sede_riferimento(self, **kwargs):
        return self.sedi_attuali(membro__in=Appartenenza.MEMBRO_DIRETTO, **kwargs).\
            order_by('-appartenenze__inizio').first()

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
        return codicefiscale.build(
            self.cognome, self.nome, self.data_nascita,
            self.genere_codice_fiscale, 'D969'
        )[0:11]

    def codice_fiscale_verosimile(self):
        """
        Controlla se il codice fiscale e' verosimile o meno
        """
        return self.genera_inizio_codice_fiscale() in self.codice_fiscale


class Privacy(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta una singola politica di Privacy selezionata da una Persona.

    ## Come creare un nuovo campo Privacy
       1. Aggiungere la costante (es. EMAIL = 'email')
       2. Aggiungere la descrizione del campo in CAMPI (es. (EMAIL, "Indirizzo E-mail"))
       3. Aggiungere la funzione lambda in CAMPO_OTTIENI (es. (EMAIL, lambda p: p.email()))
    """

    # Campi privacy
    EMAIL = 'email'
    CELLULARE = 'cellulare'
    # ... TODO

    CAMPI = (
        (EMAIL, "Indirizzo E-mail"),
        (CELLULARE, "Numeri di Cellulare"),
    )

    # Per ogni campo definire una funzione lambda
    # per ottenere il campo.
    CAMPO_OTTIENI = (
        (EMAIL, lambda p: p.email()),
        (CELLULARE, lambda p: p.cellulare())

    )
    CAMPO_OTTIENI_DICT = dict(CAMPO_OTTIENI)

    # Tipi di Policy
    # ORDINE CRESCENTE (Aperto > Ristretto)
    POLICY_PUBBLICO = 8
    POLICY_REGISTRATI = 6
    POLICY_SEDE = 4
    POLICY_RISTRETTO = 2
    POLICY_PRIVATO = 0
    POLICY = (
        (POLICY_PUBBLICO, "Pubblico"),
        (POLICY_REGISTRATI, "Utenti di Gaia"),
        (POLICY_SEDE, "A tutti i membri della mia Sede CRI"),
        (POLICY_RISTRETTO, "Ai Responsabili della mia Sede CRI"),
        (POLICY_PRIVATO, "Solo a me")
    )

    POLICY_DEFAULT = POLICY_RISTRETTO

    persona = models.ForeignKey(Persona, related_name="privacy", db_index=True)
    campo = models.CharField(max_length=8, choices=CAMPI, db_index=True)
    policy = models.PositiveSmallIntegerField(choices=POLICY, db_index=True)

    class Meta:
        verbose_name = "Politica di Privacy"
        verbose_name_plural = "Politiche di Privacy"
        unique_together = (('persona', 'campo'), )


class Telefono(ConMarcaTemporale, ModelloSemplice):
    """
    Rappresenta un numero di telefono.
    NON USARE DIRETTAMENTE. Usare i metodi in Persona.
    """

    persona = models.ForeignKey(Persona, related_name="numeri_telefono", db_index=True)
    numero = models.CharField("Numero di telefono", max_length=16)
    servizio = models.BooleanField("Numero di servizio", default=False)

    class Meta:
        verbose_name = "Numero di telefono"
        verbose_name_plural = "Numeri di telefono"
        app_label = 'anagrafica'

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
    persona = models.ForeignKey(Persona, related_name="documenti", db_index=True)
    file = models.FileField("File", upload_to=GeneratoreNomeFile('documenti/'),
                            validators=[valida_dimensione_file_8mb])

    class Meta:
        verbose_name_plural = "Documenti"
        app_label = 'anagrafica'


class Appartenenza(ModelloSemplice, ConStorico, ConMarcaTemporale, ConAutorizzazioni):
    """
    Rappresenta un'appartenenza di una Persona ad un Sede.
    """

    class Meta:
        verbose_name_plural = "Appartenenze"
        app_label = 'anagrafica'

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

    # Membri soci
    MEMBRO_SOCIO = (VOLONTARIO, ORDINARIO,)
    MEMBRO_ANZIANITA = MEMBRO_SOCIO
    MEMBRO_ANZIANITA_ANNI = 2

    # Membri sotto il diretto controllo di una altra Sede
    MEMBRO_ESTESO = (ESTESO,)

    MEMBRO = (
        (VOLONTARIO, 'Volontario'),
        (ESTESO, 'Volontario in Estensione'),
        (ORDINARIO, 'Socio Ordinario'),
        (SOSTENITORE, 'Sostenitore'),
        (DIPENDENTE, 'Dipendente'),
        (INFERMIERA, 'Infermiera Volontaria'),
        (MILITARE, 'Membro Militare'),
        (DONATORE, 'Donatore Finanziario'),
    )
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
    terminazione = models.CharField("Terminazione", max_length=1, choices=TERMINAZIONE, default=None, db_index=True,
                                    blank=True, null=True)

    # In caso di trasferimento, o altro, e' possibile individuare quale appartenenza precede
    precedente = models.ForeignKey('self', related_name='successiva', on_delete=models.SET_NULL, default=None,
                                   blank=True, null=True)

    persona = models.ForeignKey("anagrafica.Persona", related_name="appartenenze", db_index=True)
    sede = models.ForeignKey("anagrafica.Sede", related_name="appartenenze", db_index=True)

    CONDIZIONE_ATTUALE_AGGIUNTIVA = Q(confermata=True)

    RICHIESTA_NOME = "Appartenenza"

    def richiedi(self):
        """
        Richiede di confermare l'appartenenza.
        """
        # Import qui per non essere ricorsivo e rompere il mondo

        self.autorizzazione_richiedi(
            self.persona,
            (
                (PRESIDENTE, self.sede, NOTIFICA_INVIA),
                (UFFICIO_SOCI, self.sede, NOTIFICA_NON_INVIARE)
            )
        )

    def autorizzazione_concessa(self, modulo=None):
        """
        Questo metodo viene chiamato quando la richiesta viene accettata.
        :return:
        """
        # TODO: Inviare e-mail di autorizzazione concessa!

    def autorizzazione_negata(self, modulo=None):
        # TOOD: Fare qualcosa
        self.confermata = False


class SedeManager(PassThroughManagerMixin, mptt.managers.TreeManager):
    pass


class SedeQuerySet(QuerySet):

    def comitati(self):
        """
        Filtra per Comitati.
        """
        return self.filter(estensione__in=[NAZIONALE, REGIONALE, PROVINCIALE, LOCALE])

    def espandi(self, pubblici=False):
        """
        Espande il QuerySet.
        Se pubblico, me e tutte le sedi sottostanti.
        Se privato, me e le unita' territoriali incluse.
        :param pubblici: Espand i Comitati pubblici al tutti i Comitati sottostanti.
        """

        qs = self | self.filter(estensione=TERRITORIALE, genitore__in=(self.filter(estensione__in=[PROVINCIALE, LOCALE])))

        if pubblici:
            qs |= self.filter(estensione__in=[NAZIONALE, REGIONALE]).get_descendants(include_self=True)

        return qs


class Sede(ModelloAlbero, ConMarcaTemporale, ConGeolocalizzazione, ConVecchioID, ConDelegati):

    class Meta:
        verbose_name = "Sede CRI"
        verbose_name_plural = "Sedi CRI"
        app_label = 'anagrafica'

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

    objects = SedeManager.for_queryset_class(SedeQuerySet)()

    estensione = models.CharField("Estensione", max_length=1, choices=ESTENSIONE, db_index=True)
    tipo = models.CharField("Tipologia", max_length=1, choices=TIPO, default=COMITATO, db_index=True)

    # Dati del comitato
    # Nota: indirizzo e' gia' dentro per via di ConGeolocalizzazione
    telefono = models.CharField("Telefono", max_length=64, blank=True)
    fax = models.CharField("FAX", max_length=64, blank=True)
    email = models.CharField("Indirizzo e-mail", max_length=64, blank=True)
    codice_fiscale = models.CharField("Codice Fiscale", max_length=32, blank=True)
    partita_iva = models.CharField("Partita IVA", max_length=32, blank=True)

    attiva = models.BooleanField("Attiva", default=True, db_index=True)

    def sorgente_slug(self):
        if self.genitore:
            return str(self.genitore.slug) + "-" + self.nome
        else:
            return self.nome

    slug = AutoSlugField(populate_from=sorgente_slug, slugify=sede_slugify, always_update=True)
    membri = models.ManyToManyField(Persona, through='Appartenenza')

    @property
    def url(self):
        return "/informazioni/sedi/" + str(self.slug) + "/"

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

    def appartenenze_attuali(self, membro=None, figli=False, al_giorno=date.today(), **kwargs):
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
            f = Appartenenza.objects.filter(sede__in=self.get_descendants(True))
        else:
            f = self.appartenenze

        f = f.filter(
            Appartenenza.query_attuale(al_giorno).q,
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

    def membri_attuali(self, figli=False, al_giorno=date.today(), **kwargs):
        """
        Ritorna i membri attuali, eventualmente filtrati per tipo, del sede.
        :param figli: Se vero, ricerca anche tra i comitati figli.
        :param al_giorno: Default oggi. Giorno da controllare.
        :param membro: Se filtrare per membro.
        :return:
        """
        if figli:
            kwargs.update({'sede__in': self.get_descendants(True)})
        else:
            kwargs.update({'sede': self.pk})

        return Persona.objects.filter(Appartenenza.query_attuale(al_giorno=al_giorno, **kwargs).via("appartenenze"))

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

    @property
    def nome_completo(self):
        return str(self)

    def esplora(self, includi_me=True):
        """
        Ritorna un QuerySet di tutte le Sedi sottostanti.
        :param includi_me: Se True, include me stesso.
        :return: QuerySet.
        """
        return self.get_descendants(include_self=includi_me)

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
        return self.circonferenze_contenenti(Aspirante.objects.all()).count()

    def espandi(self, includi_me=False, pubblici=False):
        """
        Espande la Sede.
        Se pubblico, me e tutte le sedi sottostanti.
        Se privato, me e le unita' territoriali incluse.
        :param includi_me: Includimi nel queryset ritornato.
        :param pubblici: Espandi i pubblici, ritornando tutto al di sotto.
        """

        # Sede pubblica... ritorna tutto sotto di se.
        if pubblici and self.estensione in [NAZIONALE, REGIONALE]:
            return self.get_descendants(include_self=includi_me)

        # Sede privata... espandi con unita' territoriali.
        if self.estensione in [PROVINCIALE, LOCALE]:
            return self.get_children().filter(estensione=TERRITORIALE) | Sede.objects.filter(pk=self.pk)

        # Sede territoriale. Solo me, se richiesto.

        if includi_me:
            return Sede.objects.filter(pk=self.pk)

        else:
            return Sede.objects.none()


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

    persona = models.ForeignKey(Persona, db_index=True, related_name='deleghe', related_query_name='delega',)
    tipo = models.CharField(max_length=2, db_index=True, choices=PERMESSI_NOMI)
    oggetto_tipo = models.ForeignKey(ContentType, db_index=True)
    oggetto_id = models.PositiveIntegerField(db_index=True)
    oggetto = GenericForeignKey('oggetto_tipo', 'oggetto_id')
    firmatario = models.ForeignKey(Persona, db_index=True, null=True, default=None, related_name='deleghe_firmate',
                                   related_query_name='delega_firmata')

    def __str__(self):
        return "Delega %s di %s come %s per %s" % (
            "attuale" if self.attuale() else "passata",
            self.persona.codice_fiscale,
            self.get_tipo_display(), self.oggetto,
        )

    def permessi(self):
        """
        Ottiene un elenco di permessi che scaturiscono dalla delega.
        :return: Una lista di permessi.
        """
        return delega_permessi(self)

    def autorizzazioni(self):
        """
        Ottiene le autorizzazioni firmabili da questo ruolo.
        :return: QuerySet
        """
        oggetto_tipo = ContentType.objects.get_for_model(self.oggetto)
        return Autorizzazione.objects.filter(destinatario_ruolo=self.tipo,
                                             destinatario_oggetto_tipo__pk=oggetto_tipo.pk,
                                             destinatario_oggetto_id=self.oggetto.pk)

    def invia_notifica_creazione(self):
        return Messaggio.costruisci_e_invia(
            oggetto="%s per %s" % (self.get_tipo_display(), self.oggetto,),
            modello="email_delega_notifica_creazione.html",
            corpo={
                "delega": self,
            },
            mittente=self.firmatario,
            destinatari=[self.persona],
        )

    def invia_notifica_terminazione(self, mittente=None):
        if mittente is None:
            mittente = self.firmatario
        return Messaggio.costruisci_e_invia(
            oggetto="TERMINATO: %s per %s" % (self.get_tipo_display(), self.oggetto,),
            modello="email_delega_notifica_terminazione.html",
            corpo={
                "delega": self,
                "mittente": mittente,
            },
            mittente=mittente,
            destinatari=[self.persona],
        )


class Fototessera(ModelloSemplice, ConAutorizzazioni, ConMarcaTemporale):
    """
    Rappresenta una fototessera per la persona.
    """

    class Meta:
        verbose_name_plural = "Fototessere"

    persona = models.ForeignKey(Persona, related_name="fototessere", db_index=True)
    file = models.ImageField("Fototessera", upload_to=GeneratoreNomeFile('fototessere/'),
                             validators=[valida_dimensione_file_8mb])

    RICHIESTA_NOME = "Fototessera"


class Dimissione(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta una pratica di dimissione.
    """
    appartenenza = models.ForeignKey(Appartenenza, related_name='dimissione')


class Trasferimento(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni, ConPDF):
    """
    Rappresenta una pratica di trasferimento.
    """

    class Meta:
        verbose_name = "Richiesta di trasferimento"
        verbose_name_plural = "Richieste di trasferimento"

    richiedente = models.ForeignKey(Persona, related_name='trasferimenti_richiesti_da')
    persona = models.ForeignKey(Persona, related_name='trasferimenti')
    destinazione = models.ForeignKey(Sede, related_name='trasferimenti_destinazione')
    appartenenza = models.ForeignKey(Appartenenza, related_name='trasferimento', null=True, blank=True)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=16, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=2048, null=True, blank=False,)

    RICHIESTA_NOME = "trasferimento"

    PROTOCOLLO_AUTO = "AUTO"  # Applicato a protocollo_numero se approvazione automatica

    def autorizzazione_concedi_modulo(self):
        from anagrafica.forms import ModuloConsentiTrasferimento
        return ModuloConsentiTrasferimento

    def autorizzazione_concessa(self, modulo=None):

        # Invia notifica tramite e-mail


        app = Appartenenza(
            membro=Appartenenza.ESTESO,
            persona=self.persona,
            sede=self.destinazione,
            inizio=datetime.today(),
            fine=datetime.today() + timedelta(days=365)
        )
        app.save()
        self.appartenenza = app
        self.save()

    def richiedi(self):
        if not self.persona.sedi_attuali(membro=Appartenenza.VOLONTARIO).exists():
            raise ValueError("Impossibile richiedere trasferimento: Nessuna appartenenza attuale.")
        sede = self.persona.sedi_attuali(membro=Appartenenza.VOLONTARIO)[0]

        self.autorizzazione_richiedi(
            richiedente=self.persona,
            destinatario=(
                (PRESIDENTE, sede, NOTIFICA_INVIA),
                (UFFICIO_SOCI, sede, NOTIFICA_NON_INVIARE)
            ),
        )

    def url(self):
        return "#"

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
          nome="Trasferimento %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "trasferimento": self,
            "sede_attuale": self.persona.sedi_attuali(al_giorno=self.creazione)[0]
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

    richiedente = models.ForeignKey(Persona, related_name='estensioni_richieste_da')
    persona = models.ForeignKey(Persona, related_name='estensioni')
    destinazione = models.ForeignKey(Sede, related_name='estensioni_destinazione')
    appartenenza = models.ForeignKey(Appartenenza, related_name='estensione', null=True, blank=True)
    protocollo_numero = models.CharField('Numero di protocollo', max_length=512, null=True, blank=True)
    protocollo_data = models.DateField('Data di presa in carico', null=True, blank=True)
    motivo = models.CharField(max_length=4096, null=True, blank=False,)

    RICHIESTA_NOME = "Estensione"

    def attuale(self, **kwargs):
        """
        Controlla che l'estensione sia stata confermata e
         l'appartenenza creata sia in corso.
        """
        return self.esito == self.ESITO_OK and self.appartenenza.attuale(**kwargs)

    def autorizzazione_concedi_modulo(self):
        from anagrafica.forms import ModuloConsentiEstensione
        return ModuloConsentiEstensione

    def autorizzazione_concessa(self, modulo=None):
        app = Appartenenza(
            membro=Appartenenza.ESTESO,
            persona=self.persona,
            sede=self.destinazione,
            inizio=datetime.today(),
            fine=datetime.today() + timedelta(days=365)
        )
        app.save()
        app.richiedi()
        self.appartenenza = app
        self.save()

    def richiedi(self):
        if not self.persona.sedi_attuali(membro=Appartenenza.VOLONTARIO).exists():
            raise ValueError("Impossibile richiedere estensione: Nessuna appartenenza attuale.")
        sede = self.persona.sedi_attuali(membro=Appartenenza.VOLONTARIO)[0]

        self.autorizzazione_richiedi(
            richiedente=self.persona,
            destinatario=(
                (PRESIDENTE, sede, NOTIFICA_INVIA),
                (UFFICIO_SOCI, sede, NOTIFICA_NON_INVIARE)
            ),
        )

    def termina(self):
        self.appartenenza.fine = datetime.today()
        self.appartenenza.terminazione = Appartenenza.FINE_ESTENSIONE
        self.attuale = 'n'
        self.save()

    def genera_pdf(self):
        pdf = PDF(oggetto=self)
        pdf.genera_e_salva(
          nome="Estensione %s.pdf" % (self.persona.nome_completo, ),
          corpo={
            "estensione": self,
            "sede_attuale": self.persona.sedi_attuali(al_giorno=self.creazione)[0]
          },
          modello="pdf_estensione.html",
        )
        return pdf


class Riserva(ModelloSemplice, ConMarcaTemporale, ConStorico,
              ConAutorizzazioni, ConPDF):
    """
    Rappresenta una pratica di riserva.
    Questa puo' essere in corso o meno.
    """



class ProvvedimentoDisciplinare(ModelloSemplice, ConMarcaTemporale, ConProtocollo):
    AMMONIZIONE = "A"
    SOSPENSIONE = "S"
    ESPULSIONE = "E"
    TIPO = (
        (AMMONIZIONE, "Ammonizione",),
        (SOSPENSIONE, "Sospensione",),
        (ESPULSIONE, "Esplusione",),
    )

    motivazione = models.CharField(max_length=500)
    persona = models.ForeignKey(Persona, related_name="provvedimenti")
    tipo = models.CharField(max_length=1)

    def esegui(self, lunghezza):
        if self.tipo == "E":
            self.persona.espelli()
        if self.tipo == "S":
            sospensione = Sospensione(
                inzio=datetime.today(),
                fine=datetime.today() + timedelta(days=lunghezza),
                provvedimento=self.id
            )
            sospensione.save()


class Sospensione(ProvvedimentoDisciplinare, ConStorico):
    provvedimento = models.ForeignKey(ProvvedimentoDisciplinare, related_name="provvedimento")


