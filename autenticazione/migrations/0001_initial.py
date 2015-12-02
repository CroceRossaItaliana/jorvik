# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.', default=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, verbose_name='Indirizzo email', max_length=254)),
                ('ultimo_accesso', models.DateTimeField(verbose_name='Ultimo accesso', blank=True, null=True)),
                ('ultimo_consenso', models.DateTimeField(verbose_name='Ultimo consenso', blank=True, null=True)),
                ('is_staff', models.BooleanField(verbose_name='Amministratore', help_text="Se l'utente è un amministratore o meno.", default=False)),
                ('is_active', models.BooleanField(verbose_name='Attivo', help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', default=True)),
                ('groups', models.ManyToManyField(verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', blank=True, to='auth.Group', related_query_name='user', related_name='user_set')),
                ('persona', models.OneToOneField(to='anagrafica.Persona', blank=True, null=True)),
                ('user_permissions', models.ManyToManyField(verbose_name='user permissions', help_text='Specific permissions for this user.', blank=True, to='auth.Permission', related_query_name='user', related_name='user_set')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
