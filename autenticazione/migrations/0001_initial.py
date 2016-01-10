# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Utenza',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Indirizzo email')),
                ('ultimo_accesso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo accesso')),
                ('ultimo_consenso', models.DateTimeField(blank=True, null=True, verbose_name='Ultimo consenso')),
                ('is_staff', models.BooleanField(help_text="Se l'utente è un amministratore o meno.", default=False, verbose_name='Amministratore')),
                ('is_active', models.BooleanField(help_text='Utenti attivi. Impostare come disattivo invece di cancellare.', default=True, verbose_name='Attivo')),
                ('groups', models.ManyToManyField(help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', to='auth.Group', related_query_name='user', blank=True, verbose_name='groups')),
                ('persona', models.OneToOneField(to='anagrafica.Persona', null=True, blank=True)),
                ('user_permissions', models.ManyToManyField(help_text='Specific permissions for this user.', related_name='user_set', to='auth.Permission', related_query_name='user', blank=True, verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Utenze',
            },
        ),
    ]
