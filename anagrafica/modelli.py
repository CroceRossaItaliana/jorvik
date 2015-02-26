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
from datetime import date
from django.db.models import Q

from base.modelli import *
from base.stringhe import normalizza_nome, generatore_nome_file
from base.tratti import *
from base.stringa import *
import phonenumbers
from base.utils import is_list


class Persona(ModelloCancellabile, ConGeolocalizzazioneRaggio):
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
    # Valutiamo se mettere militare e IV tra gli stati o Appartenenze
    PERSONA = 'P'
    ASPIRANTE = 'A'
    VOLONTARIO = 'V'
    DIPENDENTE = 'D'
    MILITARE = 'M'
    INFERMIERAVOLONTARIA = 'I'
    STATO = (
        (PERSONA,       'Persona'),
        (ASPIRANTE,     'Aspirante'),
        (VOLONTARIO,    'Volontario'),
        (DIPENDENTE,    'Dipendente'),
        (MILITARE,      'Militare'),
        (INFERMIERAVOLONTARIA, 'Infermiera Volontaria'),
    )

    # Informazioni anagrafiche
    nome = models.CharField("Nome", max_length=64)
    cognome = models.CharField("Cognome", max_length=64)
    codice_fiscale = models.CharField("Codice Fiscale", max_length=16, blank=False, unique=True, db_index=True)
    data_nascita = models.DateField("Data di nascita", db_index=True)
    genere = models.CharField("Genere", max_length=1, choices=GENERE, db_index=True)

    # Stato
    stato = models.CharField("Stato", max_length=1, choices=STATO, db_index=True)

    # Informazioni anagrafiche aggiuntive - OPZIONALI (blank=True o default=..)
    comune_nascita = models.CharField("Comune di Nascita", max_length=64, blank=True)
    provincia_nascita = models.CharField("Provincia di Nascita", max_length=2, blank=True)
    stato_nascita = models.CharField("Stato di nascita", max_length=2, default="IT")
    indirizzo_residenza = models.CharField("Indirizzo di residenza", max_length=64, blank=True)
    comune_residenza = models.CharField("Comune di residenza", max_length=64, blank=True)
    provincia_residenza = models.CharField("Provincia di residenza", max_length=2, blank=True)
    stato_residenza = models.CharField("Stato di residenza", max_length=2, default="IT")
    cap_residenza = models.CharField("CAP di Residenza", max_lenght=5, blank=True)
    email_contatto = models.CharField("Email di contatto", max_length=64, blank=True)

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
    def email_utenza(self):
        """
        Restituisce l'email dell'utenza, se presente.
        :return: Email o None
        """
        if self.utenza:
            return self.utenza.email
        return None

    def __str__(self):
        return self.nome_completo()

    class Meta:
        verbose_name_plural = "Persone"

    # Q: Qual e' il numero di telefono di questa persona?
    # A: Una persona puo' avere da zero ad illimitati numeri di telefono.
    #    - Persona.numeri_telefono ottiene l'elenco di oggetti Telefono.
    #    - Per avere un elenco di numeri di telefono formattati, usare ad esempio
    #       numeri = [str(x) for x in Persona.numeri_telefono]
    #    - Usare Persona.aggiungi_numero_telefono per aggiungere un numero di telefono.

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
        t.save()
        return True


class Telefono(ModelloSemplice, ConMarcaTemporale):
    """
    Rappresenta un numero di telefono.
    NON USARE DIRETTAMENTE. Usare i metodi in Persona.
    """

    persona = models.ForeignKey(Persona, related_name="numeri_telefono")
    numero = models.CharField("Numero di telefono", max_length=16)
    servizio = models.BooleanField("Numero di servizio", default=False)

    class Meta:
        verbose_name = "Numero di telefono"
        verbose_name_plural = "Numeri di telefono"

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
    TIPO = (
        (CARTA_IDENTITA, 'Carta d\'identità'),
        (PATENTE_CIVILE, 'Patente Civile'),
        (PATENTE_CRI, 'Patente CRI'),
        (CODICE_FISCALE, 'Codice Fiscale')
    )

    persona = models.ForeignKey(Persona, related_name="documenti", db_index=True)
    file = models.FileField("File", upload_to=generatore_nome_file('documenti/'))

    class Meta:
        verbose_name_plural = "Documenti"


class Utenza(ModelloSemplice):

    class Meta:
        verbose_name_plural = "Utenze"


class Appartenenza(ModelloSemplice, ConMarcaTemporale, ConAutorizzazioni):
    """
    Rappresenta un'appartenenza di una Persona ad un Comitato.
    """

    # Tipologia appartenenza
    VOLONTARIO = 'V'
    ORDINARIO = 'O'
    DIPENDENTE = 'D'
    TIPO = (
        (VOLONTARIO, 'Volontario'),
        (ORDINARIO,  'Membro Ordinario'),
        (DIPENDENTE, 'Dipendente')
    )

    tipo = models.CharField("Tipo", max_length=1, choices=TIPO, default=VOLONTARIO, db_index=True)

    inizio = models.DateField("Inizio", db_index=True, null=False)
    fine = models.DateField("Fine", db_index=True, null=True, blank=True, default=None)

    confermata = models.BooleanField("Confermata", default=True, db_index=True)

    @staticmethod
    def query_attuale(al_giorno=date.today()):
        """
        Restituisce l'oggetto Q per filtrare le appartenenze attuali.
        :param al_giorno: Giorno per considerare l'appartenenza attuale. Default oggi.
        :return: Q!
        """

        # IMPORTANTE: Ogni modifica a questa funzione deve essere rispecchiata
        #             nella funzione Appartenenza.attuale.
        return Q(
            Q(inizio__lte=al_giorno),
            Q(fine__isnull=True) | Q(fine__gte=al_giorno),
            confermata=True,
        )

    @property
    def attuale(self, al_giorno=date.today()):
        """
        Controlla che l'appartenenza sia attuale:
        1) Al giorno,
        2) Confermata.
        :param al_giorno: Default oggi. Giorno da calcolare.
        :return: Vero o falso.
        """

        # IMPORTANTE: Ogni modifica a questa funzione deve essere rispecchiata
        #             nella funzione Appartenenza.query_attuale.

        if not self.confermata:
            return False

        if al_giorno >= self.inizio and (self.fine is None or self.fine >= al_giorno):
            return True

        return False

    def richiedi(self):
        """
        Richiede di confermare l'appartenenza.
        """
        self.confermata = False
        self.save()
        self.autorizzazione_richiedi(
            self.persona,
            self.comitato.presidente()
        )

    def autorizzazione_concessa(self):
        """
        Questo metodo viene chiamato quando la richiesta viene accettata.
        :return:
        """
        self.confermata = True
        self.save()

        # TODO: Inviare e-mail di autorizzazione concessa!

    def autorizzazione_negata(self, motivo=None):
        self.confermata = False
        self.save()

    class Meta:
        verbose_name_plural = "Appartenenze"


class Comitato(ModelloAlbero, ConGeolocalizzazione):

    # Nome gia' presente in Modello Albero

    # Estensione del Comitato
    TERRITORIALE = 'T'
    LOCALE = 'L'
    PROVINCIALE = 'P'
    REGIONALE = 'R'
    NAZIONALE = 'N'
    ESTENSIONE = (
        (TERRITORIALE, 'Unità Territoriale'),
        (LOCALE,       'Comitato Locale'),
        (PROVINCIALE,  'Comitato Provinciale'),
        (REGIONALE,    'Comitato Regionale'),
        (NAZIONALE,    'Comitato Nazioanle')
    )

    # Tipologia del comitato
    COMITATO = 'C'
    MILITARE = 'M'
    TIPO = (
        (COMITATO, 'Comitato'),
        (MILITARE, 'Sede Militare'),
    )

    estensione = models.CharField("Estensione", max_length=1, choices=ESTENSIONE, db_index=True)
    tipo = models.CharField("Tipologia", max_length=1, choices=TIPO, default=COMITATO, db_index=True)

    # Dati del comitato
    # Nota: indirizzo e' gia' dentro per via di ConGeolocalizzazione
    via = models.CharField("Via", max_length=64, blank=True)
    civico = models.CharField("Civico", max_length=8, blank=True)
    comune = models.CharField("Comune", max_length=64, blank=True)
    provincia = models.CharField("Provincia", max_length=64, blank=True)
    cap = models.CharField("CAP", max_length=5, blank=True)
    telefono = models.CharField("Telefono", max_length=64, blank=True)
    fax = models.CharField("FAX", max_length=64, blank=True)
    email = models.CharField("Indirizzo e-mail", max_length=64, blank=True)
    codice_fiscale = models.CharField("Codice Fiscale", max_length=32, blank=True)
    partita_iva = models.CharField("Partita IVA", max_length=32, blank=True)

    # Q: Come ottengo i dati del comitato?
    # A: Usa la funzione Comitato.ottieni, ad esempio, Comitato.ottieni('partita_iva').
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

    class Meta:
        verbose_name_plural = "Comitati"

    def appartenenze_attuali(self, tipo=None, comitati_figli=False, al_giorno=date.today(), **kwargs):
        """
        Ritorna l'elenco di appartenenze attuali ad un determinato giorno.
        :param tipo: Se specificato, filtra per tipologia.
        :param comitati_figli: Se vero, ricerca anche tra i comitati figli.
        :param al_giorno: Default oggi. Giorno da controllare.
        :return: Ricerca filtrata per appartenenze attuali.
        """

        # Inizia la ricerca dalla mia discendenza o da me solamente?
        if comitati_figli:
            f = Appartenenza.objects.filter(comitato__in=self.get_descendants(True))
        else:
            f = self.appartenenze

        f = f.filter(
            Appartenenza.query_attuale(al_giorno),
            **kwargs
        )

        # Se richiesto, filtra per tipo (o tipi)
        if tipo is not None:
            if is_list(tipo):
                f.filter(tipo__in=tipo)
            else:
                f.filter(tipo=tipo)

        # NB: Vengono collegate via Join le tabelle Persona e Comitato per maggiore efficienza.
        return f.select_related('persona', 'comitato')

    def membri_attuali(self, tipo=None, comitati_figli=False, **kwargs):
        """
        Ritorna i membri attuali, eventualmente filtrati per tipo, del comitato.
        :param tipo: Se specificato, aggiunge un filtro per tipo
        :param comitati_figli: Se vero, ricerca anche tra i comitati figli.
        :return:
        """
        # NB: Questo e' efficiente perche' appartenenze_attuali risolve l'oggetto Persona
        #     via una Join (i.e. non viene fatta una nuova query per ogni elemento).
        a = self.appartenenze_attuali(tipo=tipo, comitati_figli=comitati_figli, **kwargs)
        return [x.persona for x in a]


class Delega(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Deleghe"
