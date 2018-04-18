"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
import logging
from smtplib import SMTPException, SMTPRecipientsRefused, SMTPResponseException, SMTPAuthenticationError

from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction, DatabaseError
from django.template.loader import get_template
from django.utils.html import strip_tags
from celery import uuid
from django.utils.text import Truncator
from lxml import html

from .tasks import invia_mail
from base.models import *
from base.tratti import *
from social.models import ConGiudizio

logger = logging.getLogger('posta')


class ErrorePosta(Exception):
    pass


class ErrorePostaTemporaneo(ErrorePosta):
    pass


class ErrorePostaFatale(ErrorePosta):
    pass


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConAllegati):

    logging = getattr(settings, 'POSTA_LOG_DEBUG', False)

    SUPPORTO_EMAIL = 'supporto@gaia.cri.it'
    SUPPORTO_NOME = 'Supporto Gaia'
    NOREPLY_EMAIL = 'noreply@gaia.cri.it'

    class Meta:
        verbose_name = "Messaggio di posta"
        verbose_name_plural = "Messaggi di posta"
        permissions = (
            ("view_messaggio", "Can view messaggio"),
        )

    LUNGHEZZA_MASSIMA_OGGETTO = 256

    # Numero massimo di tentativi di invio prima di rinunciare all'invio
    TENTATIVI_MAX = 3

    # Limite oggetto dato da RFC 2822 e' 998 caratteri in oggetto, ma ridotto per comodita
    oggetto = models.CharField(max_length=LUNGHEZZA_MASSIMA_OGGETTO, db_index=True,
                               blank=False, default="(Nessun oggetto)")
    corpo = models.TextField(blank=True, null=False, default="(Nessun corpo)")

    ultimo_tentativo = models.DateTimeField(blank=True, null=True, default=None)
    terminato = models.DateTimeField(blank=True, null=True, default=None,
                                     help_text="La data di termine dell'invio. Questa data e' impostata "
                                               "quando l'invio e' terminato con successo, oppure quando "
                                               "sono esauriti i tentativi di invio.")

    # Il mittente e' una persona o None (il sistema di Gaia)
    mittente = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True, on_delete=models.CASCADE)
    rispondi_a = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True,
                                   related_name="messaggi_come_rispondi_a", on_delete=models.CASCADE)

    # Flag per i messaggi cancellati (perche' obsoleti)
    eliminato = models.BooleanField(default=False, null=False)

    tentativi = models.IntegerField(default=0, help_text="Il numero di tentativi di invio effettuati per questo "
                                                         "messaggio. Quando questo numero supera il massimo, non "
                                                         "verranno effettuati nuovi tentativi.")

    utenza = models.BooleanField(default=False, help_text="Se l'utente possiede un'email differente da quella "
                                                          "utilizzata per il login, il messaggio viene recapito ad "
                                                          "entrambe")

    task_id = models.CharField(max_length=36, blank=True, null=True, default=None,
                               help_text="ID del task Celery per lo smistamento di questo messaggio.")

    @property
    def destinatari(self):
        """
        Ritorna la lista di tutti gli oggetti Persona destinatari di questo messaggio.
        :return:
        """
        from anagrafica.models import Persona
        return Persona.objects.filter(oggetti_sono_destinatario__messaggio=self)

    def destinatario(self, persona):
        """
        Controlla se la persona e' tra i destinatari.
        :param persona:
        :return:
        """
        return self.oggetti_destinatario.filter(persona=persona).exists()

    def primi_oggetti_destinatario(self):
        return self.oggetti_destinatario.all()[:50]

    @property
    def corpo_body(self):
        """
        Prova ad estrarre il corpo della pagina (body).
        :return:
        """
        if not self.corpo:
            return ""
        doc = html.document_fromstring(self.corpo)
        body = doc.xpath('//body')[0]
        body.tag = 'div'
        #try:
        return html.tostring(body)
        #except:
        #    return self.corpo
        #print html.parse('http://someurl.at.domain').xpath('//body')[0].text_content()

    def processa_link(self):
        """
        Controlla i link nella e-mail relativi e li rende assoluti.
        """
        doc = html.document_fromstring(self.corpo)
        links = doc.xpath('//a')
        for el in links:
            try:
                url = el.attrib['href']
                if '://' not in url:
                    el.attrib['href'] = "https://gaia.cri.it%s" % (url,)
            except KeyError:
                continue
        self.corpo = html.tostring(doc, pretty_print=True).decode('UTF-8')

    def accoda(self):
        """
        Salva e accoda il messaggio per l'invio asincrono.
        :return:
        """
        pass

    def allegati_pronti(self):
        return ()

    def log(self, *args, **kwargs):
        if self.logging:
            logger.debug(*args, **kwargs)

    def _genera_email_da_inviare(self, connessione=None):
        """
        Genera gli oggetti EmailMultiAlternatives per le email ancora da inviare per questo
         messaggio di posta.

        Nota bene: Questo metodo non controlla il numero di tentativi effettuati.
                    Inoltre, questo metodo si occupa di rimuovere tutti i destinatari invalidi
                    (ad esempio, senza un indirizzo email) e marcarli come "inviato".

        :param connessione:         Opzionale. Una connessione al backed di posta da riutilizzare.
        :return: Un generatore di tuple (Destinatario, EmailMultiAlternatives). Il primo oggetto
                 della tupla e' un oggetto Destinatario collegato a questo messaggio, oppure None
                 per un messaggio destinato al supporto di Gaia.
        """

        if self.mittente:
            mittente_nome = self.mittente.nome_completo
            mittente_email = self.mittente.email or Messaggio.NOREPLY_EMAIL

        else:
            mittente_nome = Messaggio.SUPPORTO_NOME
            mittente_email = Messaggio.SUPPORTO_EMAIL

        # Di default, il campo rispondi_a dovrebbe essere impostato all'indirizzo email del mittente
        rispondi_a = "%s <%s>" % (mittente_nome, mittente_email)

        # Se il messaggio ha un "Rispondi a" specifico, questo sovrascrive il default
        if self.rispondi_a:

            if not self.mittente:  # Se si, e nessun mittente, usa nome mittente del reply-to
                mittente_nome = self.rispondi_a.nome_completo

            rispondi_a = "%s <%s>" % (self.rispondi_a.nome_completo, self.rispondi_a.email)

        # Il mittente del messaggio di posta ha indirizzo email NOREPLY
        mittente = "%s <%s>" % (mittente_nome, Messaggio.NOREPLY_EMAIL)
        corpo_plain = strip_tags(self.corpo)

        connessione = connessione or get_connection()

        # Per ogni destinatario a cui abbiamo non e' stato inviato il messaggio
        for destinatario in self.oggetti_destinatario.all().filter(inviato=False):

            if destinatario.inviato:
                continue

            # Se la persona non ha un indirizzo di posta, segna questo oggetto Destinatario
            # come inviato e continua col prossimo Destinatario.
            if not destinatario.persona.email:
                destinatario.inviato = True
                destinatario.errore = "Nessun indirizzo email"
                destinatario.errore_codice = destinatario.ERRORE_NESSUN_INDIRIZZO
                destinatario.save()
                continue

            email_to = [destinatario.persona.email]

            # Se il messaggio deve essere inviato anche all'indirizzo di utenza
            if self.utenza:
                email_utenza = getattr(getattr(destinatario.persona, 'utenza', {}), 'email', None)
                if email_utenza != destinatario.persona.email:
                    email_to.append(email_utenza)

            # Costruisci l'oggetto email
            email = EmailMultiAlternatives(subject=self.oggetto,
                                           body=corpo_plain,
                                           from_email=mittente,
                                           reply_to=[rispondi_a],
                                           to=email_to,
                                           attachments=self.allegati_pronti(),
                                           connection=connessione)
            email.attach_alternative(self.corpo, "text/html")

            # Ritorna una tupla per questo destinatario
            yield destinatario, email

        # Se questo messaggio non ha oggetti destinatario
        if self.oggetti_destinatario.count() == 0:

            # Questo e' un messaggio per il supporto di Gaia.
            email = EmailMultiAlternatives(subject=self.oggetto,
                                           body=corpo_plain,
                                           from_email=mittente,
                                           reply_to=[rispondi_a],
                                           to=[Messaggio.SUPPORTO_EMAIL],
                                           attachments=self.allegati_pronti(),
                                           connection=connessione)
            email.attach_alternative(self.corpo, "text/html")

            # Ritorna questo oggetto
            yield None, email

    def invia(self, connessione=None):
        """
        Effettua un tentativo di invio del messaggio, utilizzando il backend di posta configurato.

        Se il messagio e' gia' segnato come "terminato", verra' ignorato. Il metodo incrementera' il contatore
        dei tentativi di invio. Se il contatore supera il limite configurato, verra' segnato come
        "terminato".

        :param connessione:         Opzionale. Una connessione al backend di posta da riutilizzare.
        :return:                    True se l'invio e' terminato per questo messaggio, False se
                                     e' necessario provare nuovamente.
        """
        # Assicurati che il contenuto di questo messaggio sia aggiornato dal database.
        self.refresh_from_db()

        # Se il messaggio e' gia' stato inviato
        if self.terminato:
            return

        # Incrementa il contatore dei tentativi
        self.ultimo_tentativo = timezone.now()
        self.tentativi += 1

        invio_terminato = True

        # Per ognuna delle email da inviare
        email_da_inviare = self._genera_email_da_inviare(connessione=connessione)
        for destinatario, email in email_da_inviare:

            # Email al supporto di Gaia (nessun destinatario)
            if destinatario is None:
                try:
                    email.send()

                # Qualunque errore nell'inviare una email al supporto e' da considerare temporaneo
                except Exception as e:
                    logger.error(str(e))
                    invio_terminato = False

            else:  # Email con destinatario
                # Prova ad inviare l'email
                try:
                    destinatario.invia(email)

                # In caso di un errore temporaneo, maca come terminato
                except ErrorePostaTemporaneo as e:
                    invio_terminato = False
                    logger.info(str(e))

                except ErrorePostaFatale as e:
                    # Questo messaggio non e' stato inviato.
                    logger.info(str(e))
                    pass

        # Se abbiamo esaurito il numero massimo di tentativi, non provare nuovamente.
        if self.tentativi >= self.TENTATIVI_MAX:
            invio_terminato = True

        if invio_terminato:
            logger.debug("Invio terminato")
            self.terminato = timezone.now()

        self.save()
        return invio_terminato

    @classmethod
    def in_coda(cls):
        return cls.objects.filter(terminato__isnull=True).order_by('ultima_modifica')

    @classmethod
    def invia_raw(cls, oggetto, corpo_html, email_mittente,
                  reply_to=None, lista_email_destinatari=None,
                  allegati=None, fallisci_silenziosamente=False,
                  **kwargs):
        """
        Questo metodo puo' essere usato per inviare una e-mail
         immediatamente.
        """

        plain_text = strip_tags(corpo_html)
        lista_reply_to = [reply_to] if reply_to else []
        lista_email_destinatari = lista_email_destinatari or []
        allegati = allegati or []

        msg = EmailMultiAlternatives(
            subject=oggetto,
            body=plain_text,
            from_email=email_mittente,
            reply_to=lista_reply_to,
            to=lista_email_destinatari,
            **kwargs
        )
        msg.attach_alternative(corpo_html, "text/html")
        for allegato in allegati:
            msg.attach_file(allegato.file.path)
        return msg.send(fail_silently=fallisci_silenziosamente)

    @staticmethod
    def _smaltisci_coda(dimensione_massima=50):
        """
        Invia immediatamente fino a `dimensione_massima` messaggi.

        NON USARE - metodo da usare solo per i test funzionali.

        :param dimensione_massima: numero di email da smistare
        :return: None
        """
        from django.core import mail
        assert hasattr(mail, 'outbox'), 'Questo metodo è da utilzzare solo per unittest'

        messaggi = Messaggio.in_coda()

        if dimensione_massima is not None:
            messaggi = messaggi[:dimensione_massima]

        for messaggio in messaggi:
            messaggio.invia()

    @staticmethod
    def costruisci_email(oggetto='Nessun oggetto', modello='email_vuoto.html', corpo=None, mittente=None,
                         destinatari=None, allegati=None, **kwargs):
        """
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio
        """

        destinatari = destinatari or []
        allegati = allegati or []

        corpo = corpo or {}
        corpo.update({
            'mittente': mittente,
            'allegati': allegati,
        })

        oggetto = Truncator(oggetto).chars(Messaggio.LUNGHEZZA_MASSIMA_OGGETTO)

        with transaction.atomic():
            m = Messaggio(oggetto=oggetto,
                          mittente=mittente,
                          corpo=get_template(modello).render(corpo),
                          **kwargs)
            m.processa_link()
            m.save()

            for d in destinatari:
                m.oggetti_destinatario.create(persona=d)

            for a in allegati:
                a.oggetto = m
                a.save()

            return m

    @staticmethod
    def costruisci_e_invia(oggetto=None, modello=None, corpo=None, mittente=None, destinatari=None, allegati=None,
                           **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo immediatamente.
         IMPORTANTE. Non adatto per messaggi con molti destinatari. In caso di fallimento immediato, il messaggio
                     viene accodato per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio inviato.
        """

        msg = Messaggio.costruisci_email(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente,
                                         destinatari=destinatari, allegati=allegati, **kwargs)
        msg.invia()
        return msg

    @staticmethod
    def costruisci_e_accoda(oggetto=None, modello=None, corpo=None, mittente=None, destinatari=None, allegati=None,
                            **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo alla coda celery.
        :param oggetto: Oggetto deltilizzare per l'invio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :param allegati: Allegati messaggio
        :return: Un oggetto Messaggio accodato.
        """


        msg = Messaggio.costruisci_email(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente,
                                         destinatari=destinatari, allegati=allegati, **kwargs)

        # Crea un ID per il task Celery
        msg.task_id = uuid()
        msg.save()

        invia_mail.apply_async((msg.pk,), task_id=msg.task_id)

        return msg

    def __str__(self):
        return self.oggetto


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"
        permissions = (
            ("view_destinatario", "Can view destinatario"),
        )

    # Codici aggiuntivi (1000+)
    ERRORE_NESSUN_INDIRIZZO = 1001
    ERRORE_DESTINATARIO_RIFIUTATO = 1002
    ERRORE_SMTP_INASPETTATO = 1003
    ERRORE_SMTP_CONNESSIONE_FALLITA = 1004

    messaggio = models.ForeignKey(Messaggio, null=False, blank=True, related_name='oggetti_destinatario',
                                  on_delete=models.CASCADE)
    persona = models.ForeignKey("anagrafica.Persona", null=True, blank=True, default=None,
                                related_name='oggetti_sono_destinatario', on_delete=models.CASCADE)

    inviato = models.BooleanField(default=False, db_index=True,
                                  help_text="Indica se l'email per questo destinatario e' stata inviata,")

    invalido = models.BooleanField(default=False, db_index=True,
                                   help_text="Indica se il destinatario e' invalido.")

    tentativo = models.DateTimeField(default=None, blank=True, null=True, db_index=True,
                                     help_text="La data dell'ultimo tentativo di invio.")

    errore = models.CharField(max_length=512, blank=True, null=True, default=None, db_index=True,
                              help_text="Una stringa che descrive l'errore di invio, se alcuno.")
    errore_codice = models.PositiveSmallIntegerField(default=None, blank=True, null=True, db_index=True,
                                                     help_text="Un codice numerico che rappresenta l'errore.")

    def invia(self, email):
        """
        Invia una email e aggiorna questo oggetto Destinatario con il risultato
         dell'operazione di invio.

        Questo metodo non controlla se l'invio e' gia' stato effettuato o meno - e'
         responsabilita' del codice chiamante assicurarsi di non effettuare tentativi inutili
         e/o duplicati, controllando che `Destinatario.inviato` sia False.

        :param email:   Un oggetto EmailMultiAlternatives pronto all'invio.
        :throws ErrorePostaTemporaneo:  Nel caso di un errore temporaneo. E' possibile riprovare piu' tardi.
        :throws ErrorePostaFatale:      Nel caso di un errore fatale con l'invio (ad esempio, indirizzo di posta
                                         malformato). Non provare nuovamente.
        """

        logger.debug("Tentativo di invio per messaggio=%d, destinatario=%d" % (self.messaggio.pk,
                                                                               self.pk,))
        self.tentativo = timezone.now()

        try:
            email.send()

        # Errore di connessione al server SMTP
        except ConnectionError as e:
            self.errore = str(e)
            self.errore_codice = self.ERRORE_SMTP_CONNESSIONE_FALLITA
            self.inviato = False
            self.invalido = False
            self.save()
            logger.info("ErrorePostaTemporaneo: ConnectionError")
            raise ErrorePostaTemporaneo("Errore di connessione al server SMTP")

        # Il server di posta ha rifiutato alcuni di questi indirizzi
        except SMTPRecipientsRefused as e:
            self.errore = str(e)
            self.errore_codice = self.ERRORE_DESTINATARIO_RIFIUTATO
            self.invalido = True
            self.inviato = True
            self.save()
            logger.info("ErrorePostaFatale: Indirizzo destinatario invalido")
            raise ErrorePostaFatale("Indirizzo destinatario invalido")

        # Errore SMTP con codice di errore
        except SMTPResponseException as e:
            self.errore = e.smtp_error
            self.errore_codice = e.smtp_code

            # Errore fatale
            if not isinstance(e, SMTPAuthenticationError) and ((e.smtp_code // 100) == 5):
                self.invalido = False
                self.inviato = False
                self.save()
                logger.info("ErrorePostaFatale: Errore SMTP fatale (5XX)")
                raise ErrorePostaFatale("Errore SMTP fatale (5XX)")

            else:
                self.invalido = False
                self.inviato = False
                self.save()
                logger.info("ErrorePostaTemporaneo: Errore SMTP non fatale")
                raise ErrorePostaTemporaneo("Errore SMTP non fatale")

        except SMTPException as e:
            self.errore = str(e)
            self.errore_codice = self.ERRORE_SMTP_INASPETTATO
            self.invalido = False
            self.inviato = False
            self.save()
            logger.info("ErrorePostaTemporaneo: Errore SMTP inaspettato: %s" % (self.errore,))
            raise ErrorePostaTemporaneo("Errore SMTP inaspettato: %s" % (self.errore,))

        # Messaggio inviato correttamente
        self.inviato = True
        self.errore = None
        self.errore_codice = None
        self.invalido = False
        self.save()
        logger.debug("OK. Email inviata correttamente.")
