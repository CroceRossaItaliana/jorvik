# coding=utf-8

from django.contrib.auth.models import PermissionsMixin, BaseUserManager, AbstractBaseUser
from django.core.mail import send_mail
from django.db import models
from django.db.models import OneToOneField
from django.utils.http import urlquote
from base.models import ModelloSemplice
from base.tratti import ConMarcaTemporale


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


class Utenza(PermissionsMixin, AbstractBaseUser, ConMarcaTemporale):

    class Meta:
        verbose_name_plural = "Utenze"
        app_label = 'autenticazione'

    email = models.EmailField('Indirizzo email', max_length=254, unique=True)
    persona = OneToOneField("anagrafica.Persona", null=True, blank=True, db_index=True)

    is_staff = models.BooleanField('Amministratore', default=False,
        help_text='Se l\'utente è un amministratore o meno.')
    is_active = models.BooleanField('Attivo', default=True,
        help_text='Utenti attivi. Impostare come disattivo invece di cancellare.')

    objects = GestoreUtenti()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_absolute_url(self):
        return "/utenti/%s/" % urlquote(self.email)

    def get_full_name(self):
        if self.persona:
            return self.persona.nome_completo()
        return "Scollegato #" + str(self.id)

    def get_short_name(self):
        if self.persona:
            return self.persona.nome
        return "Scollegato #" + str(self.id)

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])


