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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, verbose_name='Indirizzo email', max_length=254)),
                ('ultimo_accesso', models.DateTimeField(null=True, blank=True, verbose_name='Ultimo accesso')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Amministratore', help_text="Se l'utente è un amministratore o meno.")),
                ('is_active', models.BooleanField(default=True, verbose_name='Attivo', help_text='Utenti attivi. Impostare come disattivo invece di cancellare.')),
                ('groups', models.ManyToManyField(blank=True, related_query_name='user', verbose_name='groups', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group')),
                ('persona', models.OneToOneField(blank=True, null=True, to='anagrafica.Persona')),
                ('user_permissions', models.ManyToManyField(blank=True, related_query_name='user', verbose_name='user permissions', related_name='user_set', help_text='Specific permissions for this user.', to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
