# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Indirizzo email')),
                ('ultimo_accesso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo accesso')),
                ('ultimo_consenso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo consenso')),
                ('is_staff', models.BooleanField(default=False, help_text="Se l'utente è un amministratore o meno.", verbose_name='Amministratore')),
                ('is_active', models.BooleanField(default=True, help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', verbose_name='Attivo')),
                ('groups', models.ManyToManyField(blank=True, related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups', related_name='user_set', to='auth.Group')),
                ('persona', models.OneToOneField(blank=True, null=True, to='anagrafica.Persona')),
                ('user_permissions', models.ManyToManyField(blank=True, related_query_name='user', help_text='Specific permissions for this user.', verbose_name='user permissions', related_name='user_set', to='auth.Permission')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
