# coding=utf-8
import calendar
from datetime import datetime

import jwt
from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.mail import send_mail
from django.db import models
from django.db.models import OneToOneField
from django.utils.http import urlquote
from django_otp import devices_for_user
from future.backports.datetime import timedelta

from anagrafica.validators import valida_email_personale
from base.models import ModelloSemplice
from base.stringhe import genera_uuid_casuale
from base.tratti import ConMarcaTemporale
from jorvik.settings import CRI_APP_SECRET, CRI_APP_TOKEN_EXPIRE
from posta.models import Messaggio


class GestoreUtenti(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Un utente deve avere un indirizzo email')

        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)


class Utenza(PermissionsMixin, AbstractBaseUser, ConMarcaTemporale):

    objects = GestoreUtenti()

    class Meta:
        verbose_name_plural = "Utenze"
        app_label = 'autenticazione'
        permissions = (
            ("view_utenza", "Can view utenza"),
        )

    email = models.EmailField('Indirizzo email', max_length=254, unique=True,
                              validators=[valida_email_personale])
    persona = OneToOneField("anagrafica.Persona", null=True, blank=True, db_index=True)
    ultimo_consenso = models.DateTimeField("Ultimo consenso", blank=True, null=True)

    is_staff = models.BooleanField('Amministratore', default=False,
        help_text='Se l\'utente è un amministratore o meno.')
    is_active = models.BooleanField('Attivo', default=True,
        help_text='Utenti attivi. Impostare come disattivo invece di cancellare.')
    richiedi_2fa = models.BooleanField('Richiedi 2FA', default=False,
        help_text='Richiedi all\'utente l\'attivazione di 2FA.')
    ultima_azione = models.DateTimeField('Ultima azione', null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    MIN_PASSWORD_LENGTH = 6

    @property
    def ultimo_accesso(self):
        return self.last_login

    def get_absolute_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

    def get_full_name(self):
        if self.persona:
            return self.persona.nome_completo
        return "Scollegato #" + str(self.id)

    def nome_completo(self):
        return self.get_full_name()

    @property
    def nome(self):
        return self.get_short_name()

    def get_short_name(self):
        if self.persona:
            return self.persona.nome
        return "Scollegato #" + str(self.id)

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def genera_credenziali(self, richiedente=None):
        nuova_password = genera_uuid_casuale()
        self.set_password(nuova_password)
        self.save()

        Messaggio.costruisci_e_invia(
            oggetto="Credenziali per accedere a Gaia",
            modello="email_credenziali.html",
            corpo={
                "nuova_password": nuova_password,
                "utenza": self,
                "persona": self.persona,
                "richiedente": richiedente,
            },
            mittente=None,
            destinatari=[self.persona],
        )


    @property
    def applicazioni_disponibili(self):
        """
        Ritorna un elenco di applicazioni disponibili all'utenza
        :return: dict (slug, verbose name)
        """
        if not self.persona:
            return None
        return self.persona.applicazioni_disponibili

    @property
    def richiedi_attivazione_2fa(self):
        return self.richiedi_2fa and not list(devices_for_user(self))

    @property
    def qr_login(self):
        current_datetime = datetime.utcnow()

        future_datetime = current_datetime + timedelta(minutes=CRI_APP_TOKEN_EXPIRE)
        future_timetuple = future_datetime.timetuple()

        exp = calendar.timegm(future_timetuple)

        token = jwt.encode({"email": self.email, "exp": exp}, CRI_APP_SECRET, algorithm="HS256")
        return 'gaiapp://login/' + token.decode('utf-8')
