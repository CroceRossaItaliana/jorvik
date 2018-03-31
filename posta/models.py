"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
import logging

from smtplib import SMTPException, SMTPResponseException, SMTPServerDisconnected, SMTPRecipientsRefused
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives, get_connection
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import force_text
from django.utils.html import strip_tags

from base.models import *
from base.tratti import *
from social.models import ConGiudizio
from lxml import html

logger = logging.getLogger('posta')


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
    CARATTERI_RIDUZIONE_OGGETTTO = '...'

    # Limite oggetto dato da RFC 2822 e' 998 caratteri in oggetto, ma ridotto per comodita
    oggetto = models.CharField(max_length=LUNGHEZZA_MASSIMA_OGGETTO, db_index=True,
                               blank=False, default="(Nessun oggetto)")
    corpo = models.TextField(blank=True, null=False, default="(Nessun corpo)")

    ultimo_tentativo = models.DateTimeField(blank=True, null=True, default=None)
    terminato = models.DateTimeField(blank=True, null=True, default=None)

    # Il mittente e' una persona o None (il sistema di Gaia)
    mittente = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True, on_delete=models.CASCADE)
    rispondi_a = models.ForeignKey("anagrafica.Persona", default=None, null=True, blank=True,
                                   related_name="messaggi_come_rispondi_a", on_delete=models.CASCADE)

    # Flag per i messaggi cancellati (perche' obsoleti)
    eliminato = models.BooleanField(default=False, null=False)

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

    def _processa_link(self):
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

    def invia(self, connection=None, utenza=False):
        """
        Salva e invia immediatamente il messaggio.
        :return:
        """
        self.save()  # Assicurati che sia salvato

        connection = connection or get_connection()

        if self.mittente is None:
            mittente_nome = self.SUPPORTO_NOME
            mittente_email = self.SUPPORTO_EMAIL
        else:
            mittente_nome = self.mittente.nome_completo
            mittente_email = self.mittente.email
            if not mittente_email:
                mittente_email = self.NOREPLY_EMAIL

        if self.rispondi_a:  # Rispondi a definito?
            if not self.mittente:  # Se si, e nessun mittente, usa nome mittente del reply-to
                mittente_nome = self.rispondi_a.nome_completo
            reply_to = "%s <%s>" % (self.rispondi_a.nome_completo, self.rispondi_a.email)

        else:  # Altrimenti, imposta reply-to allo stesso mittente.
            reply_to = "%s <%s>" % (mittente_nome, mittente_email)

        mittente = "%s <%s>" % (mittente_nome, self.NOREPLY_EMAIL)

        plain_text = strip_tags(self.corpo)
        successo = True

        if self.logging:
            logger.debug('MSG %s: Inizio: Oggetto=%s' % (self.pk, self.oggetto))
        # E-mail al supporto
        if not self.oggetti_destinatario.all().exists():
            try:
                msg = EmailMultiAlternatives(
                    subject=self.oggetto,
                    body=plain_text,
                    from_email=mittente,
                    reply_to=[reply_to],
                    to=[self.SUPPORTO_EMAIL],
                    attachments=self.allegati_pronti(),
                    connection=connection,
                )
                msg.attach_alternative(self.corpo, "text/html")
                msg.send()
            except SMTPException as e:
                if self.logging:
                    logger.debug('MSG %s: errore grave %s' % (self.pk, e))
                successo = False

        # E-mail a delle persone
        if self.logging:
            logger.debug('MSG %s: Destinatari=%d' % (self.pk, self.oggetti_destinatario.filter(inviato=False).count()))
        if not self.oggetti_destinatario.filter(inviato=False).exists():
            successo = True
        for d in self.oggetti_destinatario.filter(inviato=False):
            destinatari = []
            if hasattr(d, 'persona') and d.persona and d.persona.email:
                destinatari.append(d.persona.email)
            if hasattr(d.persona, 'utenza') and d.persona.utenza and d.persona.utenza.email:
                if utenza and d.persona.utenza.email != d.persona.email:
                    destinatari.append(d.persona.utenza.email)

            if self.logging:
                logger.debug('MSG %s: Num=%d Destinatari=%s' % (self.pk, len(destinatari), d.pk))
                # si usa la funzione interna hash, è più stupida ma serve solo per controllare la presenza ripetuta
                # di email nel log
                logger.debug('MSG %s: Hash destinatari=%s' % (self.pk, ','.join([str(hash(email)) for email in destinatari])))
            # Non diamo per scontato che esistano destinatari
            if destinatari:
                # Assicurati che la connessione sia aperta
                connection.open()

                # Evita duplicati in invii lunghi (se ci sono problemi con lock)...
                d.refresh_from_db()
                if d.inviato:
                    if self.logging:
                        logger.debug('MSG %s: destinatario duplicato: msg=%s, dest=%s' % (self.pk, self.oggetto, ','.join(destinatari)))
                    print("%s  (*) msg=%d, dest=%d, protezione invio duplicato" % (
                        datetime.now().isoformat(' '),
                        self.pk,
                        d.pk,
                    ))
                    continue

                try:
                    msg = EmailMultiAlternatives(
                        subject=self.oggetto,
                        body=plain_text,
                        from_email=mittente,
                        reply_to=[reply_to],
                        to=destinatari,
                        attachments=self.allegati_pronti(),
                        connection=connection,
                    )
                    msg.attach_alternative(self.corpo, "text/html")
                    msg.send()
                    d.inviato = True

                except SMTPException as e:
                    if self.logging:
                        logger.debug('MSG %s: eccezione %s' % (self.pk, e,))

                    if isinstance(e, SMTPRecipientsRefused):
                        try:
                            if any([code == 250 for email, code in e.recipients.items()]):
                                # Almeno un'email è partita, il messaggio si considera inviato
                                d.inviato = True
                                successo = True
                            else:
                                # E-mail di destinazione rotta: ignora.
                                d.inviato = True
                                d.invalido = True
                        except AttributeError:
                            # E-mail di destinazione rotta: ignora.
                            d.inviato = True
                            d.invalido = True

                    elif isinstance(e, SMTPResponseException) and e.smtp_code == 501:
                        # E-mail di destinazione rotta: ignora.
                        d.inviato = True
                        d.invalido = True

                    elif isinstance(e, SMTPServerDisconnected):
                        # Se il server si e' disconnesso, riconnetti.
                        successo = False  # Questo messaggio verra' inviato al prossimo tentativo.
                        connection.close()  # Chiudi handle alla connessione
                        connection.open()  # Riconnettiti

                    else:
                        successo = False  # Altro errore... riprova piu' tardi.

                    d.errore = str(e)

                except TypeError as e:
                    if self.logging:
                        logger.debug('MSG %s: eccezione %s' % (self.pk, e,))
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Nessun indirizzo e-mail. Saltato"

                except AttributeError as e:
                    if self.logging:
                        logger.debug('MSG %s: eccezione %s' % (self.pk, e,))
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Destinatario non valido. Saltato"

                except UnicodeEncodeError as e:
                    if self.logging:
                        logger.debug('MSG %s: eccezione %s' % (self.pk, e,))
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Indirizzo e-mail non valido. Saltato."

                if not d.inviato or d.invalido:
                    if self.logging:
                        logger.debug('MSG %s: errore invio destinatario=%s, errore=%s' % (self.pk, d.pk, d.errore))
                    print("%s  (!) errore invio id=%d, destinatario=%d, errore=%s" % (
                        datetime.now().isoformat(' '),
                        self.pk,
                        d.pk,
                        d.errore,
                    ))
                d.tentativo = datetime.now()
                d.save()
                if self.logging:
                    logger.debug('MSG %s: salvataggio destinatario=%s' % (self.pk, d.pk))
                    logger.debug('MSG %s: termine invio successo=%s, inviato=%s invalido=%s errore=%s' % (self.pk, successo, d.inviato, d.invalido, d.errore))

        if successo:
            self.terminato = datetime.now()

        self.ultimo_tentativo = datetime.now()
        if self.logging:
            logger.debug('MSG %s: salvataggio terminato=%s ultimo_tentativo=%s' % (self.pk, self.terminato, self.ultimo_tentativo))
        self.save()

    def aggiungi_destinatario(self, persona):
        """
        Aggiunge un destinatario al messaggio di posta.
        Il messaggio DEVE essere salvato.
        :param persona: La Persona da aggiungere.
        :return:
        """
        d = Destinatario(messaggio=self, persona=persona)
        return d.save()

    @classmethod
    def in_coda(cls):
        return cls.objects.filter(terminato=None).order_by('ultima_modifica')

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

    @classmethod
    def smaltisci_coda(cls, dimensione_massima=50):
        da_smaltire = cls.in_coda()[:dimensione_massima]
        print("%s == ricerca messaggi da smaltire, coda=%d" % (
            datetime.now().isoformat(' '),
            dimensione_massima,
        ))
        totale = 0
        print("%s apro connessione al backed di invio posta" % (
            datetime.now().isoformat(' '),
        ))
        connection = get_connection()
        for messaggio in da_smaltire:
            totale += 1
            if cls.logging:
                logger.debug('MSG %s: pickup destinatari=(totale=%d, in_attesa=%d)' % (
                    messaggio.pk, messaggio.oggetti_destinatario.all().count(),
                    messaggio.oggetti_destinatario.filter(inviato=False).count(),
                ))
            print("%s invio messaggio id=%d, destinatari=(totale=%d, in_attesa=%d)" % (
                datetime.now().isoformat(' '),
                messaggio.pk,
                messaggio.oggetti_destinatario.all().count(),
                messaggio.oggetti_destinatario.filter(inviato=False).count(),
            ))
            messaggio.invia(connection)
        print("%s -- fine elaborazione, elaborati=%d" % (
            datetime.now().isoformat(' '),
            totale,
        ))


    @classmethod
    def costruisci(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], allegati=[], **kwargs):

        corpo.update({
            "mittente": mittente,
            "allegati": allegati,
        })

        # Accorcia l'oggetto se necessario.
        if len(oggetto) > cls.LUNGHEZZA_MASSIMA_OGGETTO:
            oggetto = oggetto[:(cls.LUNGHEZZA_MASSIMA_OGGETTO - len(cls.CARATTERI_RIDUZIONE_OGGETTTO))]
            oggetto = "%s%s" % (oggetto, cls.CARATTERI_RIDUZIONE_OGGETTTO)

        m = cls(
            oggetto=oggetto,
            mittente=mittente,
            corpo=get_template(modello).render(corpo),
            **kwargs
        )
        m._processa_link()
        m.save()

        # Se QuerySet, rendi distinti.
        if isinstance(destinatari, QuerySet):
            destinatari = destinatari.distinct()

        for d in destinatari:
            m.aggiungi_destinatario(d)

        for a in allegati:
            a.oggetto = m
            a.save()

        return m

    @classmethod
    def costruisci_e_invia(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], allegati=[], utenza=False, **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e inviarlo immediatamente.
         IMPORTANTE. Non adatto per messaggi con molti destinatari. In caso di fallimento immediato, il messaggio
                     viene accodato per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :return: Un oggetto Messaggio inviato.
        """
        m = cls.costruisci(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente, destinatari=destinatari, allegati=allegati, **kwargs)
        m.invia(utenza=utenza)
        return m

    @classmethod
    def costruisci_e_accoda(cls, oggetto='Nessun oggetto', modello='email_vuoto.html', corpo={}, mittente=None, destinatari=[], allegati=[], **kwargs):
        """
        Scorciatoia per costruire rapidamente un messaggio di posta e accodarlo per l'invio asincrono.
        :param oggetto: Oggetto del messaggio.
        :param modello: Modello da utilizzare per l'invio.
        :param corpo: Sostituzioni da fare nel modello. Dizionario {nome: valore}
        :param mittente: Mittente del messaggio. None per Notifiche da Gaia.
        :param destinatari: Un elenco di destinatari (oggetti Persona).
        :return: Un oggetto Messaggio accodato.
        """
        m = cls.costruisci(oggetto=oggetto, modello=modello, corpo=corpo, mittente=mittente, destinatari=destinatari, allegati=[], **kwargs)
        m.accoda()
        return m

    def __str__(self):
        return self.oggetto


class Destinatario(ModelloSemplice, ConMarcaTemporale):

    class Meta:
        verbose_name = "Destinatario di posta"
        verbose_name_plural = "Destinatario di posta"
        permissions = (
            ("view_destinatario", "Can view destinatario"),
        )

    messaggio = models.ForeignKey(Messaggio, null=False, blank=True, related_name='oggetti_destinatario',
                                  on_delete=models.CASCADE)
    persona = models.ForeignKey("anagrafica.Persona", null=True, blank=True, default=None,
                                related_name='oggetti_sono_destinatario', on_delete=models.CASCADE)

    inviato = models.BooleanField(default=False, db_index=True)
    invalido = models.BooleanField(default=False, db_index=True)
    tentativo = models.DateTimeField(default=None, blank=True, null=True, db_index=True)
    errore = models.CharField(max_length=256, blank=True, null=True, default=None, db_index=True)
