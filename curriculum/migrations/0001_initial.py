# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Titolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('vecchio_id', models.IntegerField(db_index=True, default=None, blank=True, null=True)),
                ('tipo', models.CharField(db_index=True, choices=[('CP', 'Competenza Personale'), ('PP', 'Patente Civile'), ('PC', 'Patente CRI'), ('TS', 'Titolo di Studio'), ('TC', 'Titolo CRI')], max_length=2)),
                ('richiede_conferma', models.BooleanField(default=False)),
                ('richiede_data_ottenimento', models.BooleanField(default=False)),
                ('richiede_luogo_ottenimento', models.BooleanField(default=False)),
                ('richiede_data_scadenza', models.BooleanField(default=False)),
                ('richiede_codice', models.BooleanField(default=False)),
                ('inseribile_in_autonomia', models.BooleanField(default=True)),
                ('nome', models.CharField(db_index=True, max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='TitoloPersonale',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('creazione', models.DateTimeField(db_index=True, auto_now_add=True)),
                ('ultima_modifica', models.DateTimeField(db_index=True, auto_now=True)),
                ('confermata', models.BooleanField(db_index=True, default=True, verbose_name='Confermata')),
                ('ritirata', models.BooleanField(db_index=True, default=False, verbose_name='Ritirata')),
                ('data_ottenimento', models.DateField(help_text="Data di ottenimento del Titolo o Patente. Ove applicabile, data dell'esame.", blank=True, null=True)),
                ('luogo_ottenimento', models.CharField(help_text='Luogo di ottenimento del Titolo o Patente. Formato es.: Roma (RM).', max_length=255, blank=True, null=True)),
                ('data_scadenza', models.DateField(help_text='Data di scadenza del Titolo o Patente.', blank=True, null=True)),
                ('codice', models.CharField(db_index=True, help_text='Codice/Numero identificativo del Titolo o Patente. Presente sul certificato o sulla Patente.', max_length=128, blank=True, null=True)),
                ('codice_corso', models.CharField(db_index=True, max_length=128, blank=True, null=True)),
                ('certificato', models.BooleanField(default=False)),
                ('certificato_da', models.ForeignKey(to='anagrafica.Persona', null=True, related_name='titoli_da_me_certificati')),
                ('persona', models.ForeignKey(related_name='titoli_personali', to='anagrafica.Persona')),
                ('titolo', models.ForeignKey(to='curriculum.Titolo')),
            ],
            options={
                'verbose_name': 'Titolo personale',
                'verbose_name_plural': 'Titoli personali',
            },
        ),
    ]
