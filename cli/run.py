import os

import click
import pandas as pd 
import numpy as np

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jorvik.settings")
django.setup()

from anagrafica.models import Sede, Persona, Appartenenza
from autenticazione.models import Utenza
from base.utils import poco_fa

class ImportProcedure:

    def __init__(self, file_path, dryrun, force_default=None):
        self.file_path = file_path
        self.dryrun = dryrun
        self.force_default = force_default

        self.dataset = pd.read_csv(file_path, sep=';', error_bad_lines=False, keep_default_na=False, na_values=None)

    def echo_stats(self):
        click.echo("Dataframe shape: {}".format(self.dataset.shape))

    def apply(self):
        sede = None
        skipped = []
        evaluated = 0
        inserted = []
        really_inserted = []

        for index, row in self.dataset.iterrows():
            evaluated += 1
            if not row['Mail']:
                click.echo('No e-mail... skip')
                skipped.append(row['Codice Fiscale'])
                continue

            persona_dict = {"nome": row['Nome'], 
                            "cognome": row['Cognome'], 
                            "codice_fiscale": row['Codice Fiscale'], 
                            "data_nascita": row['Data Nascita'], 
                            "email_contatto": row['Mail'], 
                            "note": row['note su registrazione'], 
                            "indirizzo_residenza": row['Indirizzo di Residenza'], 
                            "cm": False, "iv": False,
                            "comune_residenza": row['Comune di Residenza'], 
                            "provincia_residenza": row['Provincia di Residenza'], 
                            "cap_residenza": '-'}
            
            if self.force_default:
                persona_dict.update(self.force_default)

            sede = row['sede'] #Sede.objects.get(id=row['sede'])

            # riga di anteprima
            click.echo("Working on {}".format(persona_dict.get('Codice Fiscale')))
            #click.echo(persona_dict)

            try:
                persona = Persona.objects.get(codice_fiscale__iexact=row['Codice Fiscale'])
            except Persona.DoesNotExist:
                persona = Persona(**persona_dict)
                inserted.append(row['Codice Fiscale'])
                if self.dry_run:                    
                    click.echo('Dry run skip creating persona')
                else:
                    really_inserted.append(row['Codice Fiscale'])
                    persona.save()

            if self.dry_run:
                click.echo('Dry run skip creating apertenenza to {}'.format(sede))                
            if not dry_run:
                inizio_appartenenza = None
                Appartenenza.objects.create(persona=persona, sede=sede, inizio=inizio_appartenenza,
                                            membro=Appartenenza.DIPENDENTE)

            if not Utenza.objects.filter(persona=persona).exists():
                # Non ha utenza
                if not Utenza.objects.filter(email__iexact=persona.email_contatto):
                    # Non esiste, prova a creare
                    u = Utenza(persona=persona, email=persona.email_contatto)
                    if self.dry_run:
                        click.echo('Dry run skip creating user')
                    if not self.dry_run:
                        u.save()
                        u.genera_credenziali()
            
        click.echo('Finish. Evaluated {}, Skipped {}, Inserted {}'.format(evaluated, len(skipped), len(inserted)))


@click.command()
@click.option('--dryrun', is_flag=True, help='print only apache template')
@click.argument('file_path')
def main(dryrun, file_path):
    click.echo("Caricamento dati da file {}. Dryrun: {}".format(file_path, dryrun))
    
    p = ImportProcedure(file_path, dryrun, force_default=dict(cm=True))
    p.echo_stats()
    
    if click.confirm("Procediamo? "):
        p.apply()


if __name__ == '__main__':
    main()
