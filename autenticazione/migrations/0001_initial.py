# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status', default=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(verbose_name='Indirizzo email', unique=True, max_length=254)),
                ('ultimo_accesso', models.DateTimeField(null=True, verbose_name='Ultimo accesso', blank=True)),
                ('ultimo_consenso', models.DateTimeField(null=True, verbose_name='Ultimo consenso', blank=True)),
                ('is_staff', models.BooleanField(help_text="Se l'utente è un amministratore o meno.", verbose_name='Amministratore', default=False)),
                ('is_active', models.BooleanField(help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', verbose_name='Attivo', default=True)),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', blank=True, related_name='user_set', verbose_name='groups', to='auth.Group')),
                ('persona', models.OneToOneField(null=True, blank=True, to='anagrafica.Persona')),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', related_query_name='user', blank=True, related_name='user_set', verbose_name='user permissions', to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
