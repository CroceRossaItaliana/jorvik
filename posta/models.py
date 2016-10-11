"""
Questo modulo definisce i modelli del modulo di Posta di Gaia.
"""
from smtplib import SMTPException, SMTPResponseException, SMTPServerDisconnected, SMTPRecipientsRefused
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives, get_connection
from django.db.models import QuerySet
from django.template import Context
from django.template.loader import get_template
from django.utils.html import strip_tags

from base.models import *
from base.tratti import *
from social.models import ConGiudizio
from lxml import html


class Messaggio(ModelloSemplice, ConMarcaTemporale, ConGiudizio, ConAllegati):

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
            except SMTPException:
                successo = False

        # E-mail a delle persone
        for d in self.oggetti_destinatario.filter(inviato=False):
            destinatari = []
            if hasattr(d, 'persona') and d.persona:
                destinatari.append(d.persona.email)
            if hasattr(d.persona, 'utenza') and d.persona.utenza:
                if utenza and d.persona.utenza.email != d.persona.email:
                    destinatari.append(d.persona.utenza.email)

            # Non diamo per scontato che esistano destinatari
            if destinatari:
                # Assicurati che la connessione sia aperta
                connection.open()

                # Evita duplicati in invii lunghi (se ci sono problemi con lock)...
                d.refresh_from_db()
                if d.inviato:
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

                    if isinstance(e, SMTPRecipientsRefused):
                        if any([list(item.values())[0] == 250 for item in e.recipients]):
                            d.inviato = True
                            successo = True  # Almeno un'email è partita, il messaggio si considera inviato
                        else:
                            d.inviato = True  # E-mail di destinazione rotta: ignora.
                            d.invalido = True

                    elif isinstance(e, SMTPResponseException) and e.smtp_code == 501:
                        d.inviato = True  # E-mail di destinazione rotta: ignora.
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
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Nessun indirizzo e-mail. Saltato"

                except AttributeError as e:
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Destinatario non valido. Saltato"

                except UnicodeEncodeError as e:
                    d.inviato = True
                    d.invalido = True
                    d.errore = "Indirizzo e-mail non valido. Saltato."

                if not d.inviato or d.invalido:
                    print("%s  (!) errore invio id=%d, destinatario=%d, errore=%s" % (
                        datetime.now().isoformat(' '),
                        self.pk,
                        d.pk,
                        d.errore,
                    ))

                d.tentativo = datetime.now()
                d.save()

        if successo:
            self.terminato = datetime.now()

        self.ultimo_tentativo = datetime.now()
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
