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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(verbose_name='Indirizzo email', unique=True, max_length=254)),
                ('ultimo_accesso', models.DateTimeField(verbose_name='Ultimo accesso', blank=True, null=True)),
                ('ultimo_consenso', models.DateTimeField(verbose_name='Ultimo consenso', blank=True, null=True)),
                ('is_staff', models.BooleanField(verbose_name='Amministratore', default=False, help_text="Se l'utente è un amministratore o meno.")),
                ('is_active', models.BooleanField(verbose_name='Attivo', default=True, help_text='Utenti attivi. Impostare come disattivo invece di cancellare.')),
                ('groups', models.ManyToManyField(related_query_name='user', blank=True, to='auth.Group', verbose_name='groups', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('persona', models.OneToOneField(blank=True, to='anagrafica.Persona', null=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', blank=True, to='auth.Permission', verbose_name='user permissions', related_name='user_set', help_text='Specific permissions for this user.')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
