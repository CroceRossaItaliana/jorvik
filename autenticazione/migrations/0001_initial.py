# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '__first__'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Indirizzo email')),
                ('ultimo_accesso', models.DateTimeField(blank=True, verbose_name='Ultimo accesso', null=True)),
                ('ultimo_consenso', models.DateTimeField(blank=True, verbose_name='Ultimo consenso', null=True)),
                ('is_staff', models.BooleanField(default=False, help_text="Se l'utente è un amministratore o meno.", verbose_name='Amministratore')),
                ('is_active', models.BooleanField(default=True, help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', verbose_name='Attivo')),
                ('groups', models.ManyToManyField(related_query_name='user', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', verbose_name='groups', to='auth.Group')),
                ('persona', models.OneToOneField(blank=True, null=True, to='anagrafica.Persona')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', blank=True, help_text='Specific permissions for this user.', related_name='user_set', verbose_name='user permissions', to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
