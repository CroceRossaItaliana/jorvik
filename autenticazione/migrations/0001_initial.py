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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, verbose_name='Indirizzo email', max_length=254)),
                ('ultimo_accesso', models.DateTimeField(blank=True, verbose_name='Ultimo accesso', null=True)),
                ('ultimo_consenso', models.DateTimeField(blank=True, verbose_name='Ultimo consenso', null=True)),
                ('is_staff', models.BooleanField(verbose_name='Amministratore', default=False, help_text="Se l'utente è un amministratore o meno.")),
                ('is_active', models.BooleanField(verbose_name='Attivo', default=True, help_text='Utenti attivi. Impostare come disattivo invece di cancellare.')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('persona', models.OneToOneField(to='anagrafica.Persona', null=True, blank=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
