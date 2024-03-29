import logging

from django.contrib import messages

from curriculum.autocomplete_light_registry import EsperienzeProfessionaliAutocompletamento
from curriculum.forms import FormAddAltreQualifica, FormAddTitoloStudio, FormAddConoscenzeLinguistiche, \
    FormAddCompetenzeSkills
from curriculum.models import TitoloPersonale, Titolo, TitoloSpecializzazione, TitoloSkill
from formazione.validators import validate_file_type

logger = logging.getLogger(__name__)


def carica_titolo_studio(request, me, redirect_url):
    form = FormAddTitoloStudio(request.POST, request.FILES)
    if form.is_valid():
        cd = form.cleaned_data
        tipo_titolo_studio = cd['tipo_titolo_di_studio']
        if cd['attestato_file'] and validate_file_type(cd['attestato_file']) == False:
            messages.error(request, 'File non supportato')
            return redirect_url

        if tipo_titolo_studio == TitoloPersonale.SCUOLA_OBBLIGO:
            scuola_obbligo = Titolo.objects.filter(
                nome="Scuola dell'obblico", tipo=Titolo.TITOLO_STUDIO
            ).first()
            if not scuola_obbligo:
                logger.info('Creo titolo "Scuola dell\'obblico"')
                scuola_obbligo = Titolo(nome="Scuola dell'obblico", tipo=Titolo.TITOLO_STUDIO)
                scuola_obbligo.save()
            titolo_personale = TitoloPersonale(
                persona=me,
                confermata=True,
                tipo_titolo_di_studio=tipo_titolo_studio,
                titolo=scuola_obbligo,
                data_ottenimento=cd['data_ottenimento'],
                attestato_file=cd['attestato_file']
                #numero_brevetto=cd['numero_brevetto']
            )
            titolo_personale.save()
            logger.info("Creato titolo personale {}".format(titolo_personale))
        elif tipo_titolo_studio == TitoloPersonale.DIPLOMA:
            if cd['no_diploma']:
                logger.info("Titolo diploma non esistente")
                nome_titolo = cd['nuovo_diploma'].capitalize()
                diploma_titolo = Titolo(
                    nome=nome_titolo, tipo=Titolo.TITOLO_STUDIO, tipo_titolo_studio=Titolo.DIPLOMA
                )
                diploma_titolo.save()
                logger.info("Creato Titolo diploma {}".format(diploma_titolo))
            else:
                diploma_titolo = cd['diploma']

            titolo_personale = TitoloPersonale(
                persona=me,
                confermata=True,
                titolo=diploma_titolo,
                tipo_titolo_di_studio=tipo_titolo_studio,
                data_ottenimento=cd['data_ottenimento'],
                attestato_file=cd['attestato_file']
                #numero_brevetto=cd['numero_brevetto']
            )
            titolo_personale.save()
            logger.info("Creato titolo personale {}".format(titolo_personale))
        elif tipo_titolo_studio in TitoloPersonale.TITOLO_DI_STUDIO_LAUREE:
            if cd['no_laurea']:
                logger.info("Titolo laurea non esistente")
                nome_titolo = cd['nuova_laurea'].capitalize()
                laurea_titolo = Titolo(
                    nome=nome_titolo, tipo=Titolo.TITOLO_STUDIO, tipo_titolo_studio=Titolo.LAUREA
                )
                laurea_titolo.save()
                logger.info("Creato Titolo laurea {}".format(laurea_titolo))
            else:
                laurea_titolo = cd['laurea']

            titolo_personale = TitoloPersonale(
                persona=me,
                confermata=True,
                titolo=laurea_titolo,
                tipo_titolo_di_studio=tipo_titolo_studio,
                data_ottenimento=cd['data_ottenimento'],
                attestato_file=cd['attestato_file']
                #numero_brevetto=cd['numero_brevetto']
            )
            titolo_personale.save()
            logger.info("Creato titolo personale {}".format(titolo_personale))
        else:
            logger.info('tipo_titolo_studio non presente nella lista')
            messages.error(request, "Il titolo di studio non è stato inserito correttamente")
    else:
        logger.info('Errore Validazione form {}'.format(form.errors))
        messages.error(request, "Il titolo di studio non è stato inserito correttamente, correggere i dati nel form")

    return redirect_url


def carica_altri_titoli(request, me, redirect_url):

    form = FormAddAltreQualifica(request.POST, request.FILES)

    if form.is_valid():
        cd = form.cleaned_data
        tipo_altro = cd['tipo_altro_titolo']
        if cd['attestato_file'] and validate_file_type(cd['attestato_file']) == False:
            messages.error(request, "Tipo di file non supportato. Tipi di file supportati: csv, zip, rar, gif, png, jpg,  jpeg, tiff, rtf, pdf, ods, odt, doc, docx, xls, xlsx.")
            return redirect_url

        if tipo_altro == TitoloPersonale.PARTNERSHIP:
            titolo = Titolo.objects.get(pk=cd['titoli_in_partnership'])
            if cd['no_argomento']:
                argomento = cd['argomento_nome']
                argomenti = titolo.argomenti.split(',')
                argomenti.append(argomento)
                titolo.argomenti = ','.join(argomenti)
                titolo.save()
            else:
                argomento = ','.join(cd['argomento'])

            titolo_personale = TitoloPersonale(
                persona=me,
                confermata=True,
                data_ottenimento=cd['data_ottenimento'],
                titolo=Titolo.objects.get(pk=cd['titoli_in_partnership']),
                attestato_file=cd['attestato_file'],
                argomento=argomento,
                tipo_altro_titolo=cd['tipo_altro_titolo']
            )
            titolo_personale.save()
        elif tipo_altro == TitoloPersonale.ALTRO:
            no_corso = cd['no_corso']
            if not no_corso:
                titolo = cd['altri_titolo']
                if cd['no_argomento']:
                    argomento = cd['argomento_nome']
                    argomenti = titolo.argomenti.split(',')
                    argomenti.append(argomento)
                    titolo.argomenti = ','.join(argomenti)
                    titolo.save()
                else:
                    argomento = ','.join(cd['argomento'])
                titolo_personale = TitoloPersonale(
                    persona=me,
                    confermata=True,
                    data_ottenimento=cd['data_ottenimento'],
                    titolo=titolo,
                    attestato_file=cd['attestato_file'],
                    argomento=argomento,
                    tipo_altro_titolo=cd['tipo_altro_titolo']
                )
                titolo_personale.save()
            else:  # DEVO CREARE IL TITOLO
                titolo = Titolo(
                    tipo=Titolo.ALTRI_TITOLI,
                    nome=cd['nome_corso'],
                    argomenti=cd['argomento_nome']
                )
                titolo.save()
                titolo_personale = TitoloPersonale(
                    persona=me,
                    confermata=True,
                    data_ottenimento=cd['data_ottenimento'],
                    titolo=titolo,
                    attestato_file=cd['attestato_file'],
                    argomento=cd['argomento_nome'],
                    tipo_altro_titolo=cd['tipo_altro_titolo']
                )
                titolo_personale.save()
        else:
            messages.error(request, "La qualifica non è stata inserita correttamente")
            return redirect_url
    else:
        messages.error(request, "La qualifica non è stata inserita correttamente correggere i dati nel form")

    return redirect_url


def carica_conoscenze_linguistiche(request, me, redirect_url):
    logger.info('carica_conoscenze_linguistiche')
    form = FormAddConoscenzeLinguistiche(request.POST, request.FILES)

    if form.is_valid():
        cd = form.cleaned_data
        if cd['attestato_file'] is not None:
            if validate_file_type(cd['attestato_file']) == False:
                messages.error(request, 'File non supportato')
                return redirect_url

        if cd['no_lingua']:
            logger.info('Lingua campo libero')
            titolo = Titolo(
                nome=cd['nuova_lingua'].capitalize(), tipo=Titolo.CONOSCENZA_LINGUISTICHE
            )
            titolo.save()
            logger.info('Creato nuovo titolo lingua {}'.format(titolo))
        else:
            titolo = cd['lingua']
            logger.info('Lingua campo autocomplete {}'.format(titolo))

        titolo_personale = TitoloPersonale(
            persona=me,
            titolo=titolo,
            livello_linguistico_orale=cd['livello_linguistico_orale'],
            livello_linguistico_lettura=cd['livello_linguistico_lettura'],
            livello_linguistico_scrittura=cd['livello_linguistico_scrittura'],
            data_ottenimento=cd['data_ottenimento'],
            data_scadenza=cd['data_scadenza'],
            attestato_file=cd['attestato_file'],
        )
        titolo_personale.save()
        logger.info('Nuovo titolo peronale {}'.format(titolo_personale))
    else:
        messages.error(request, "La competenza linguistica non è stata inserita campo form non validi")
        logger.info('form non valido {}'.format(form.error))

    return redirect_url


def carica_esperienza_professionale(request, me, redirect_url):
    logger.info('carica_conoscenze_linguistiche')
    form = FormAddCompetenzeSkills(request.POST, request.FILES)
    if form.is_valid():
        cd = form.cleaned_data
        if cd['attestato_file'] is not None:
            if validate_file_type(cd['attestato_file']) == False:
                messages.error(request, 'File non supportato')
                return redirect_url

        if cd['no_professione']:
            logger.info('Professione campo libero')
            professione = Titolo(
                nome=cd['nuova_professione'].capitalize(),
                tipo=Titolo.ESPERIENZE_PROFESSIONALI,
                area=EsperienzeProfessionaliAutocompletamento.SETTORE_DI_RIFERIMENTO[cd['settore_di_riferimento']]
            )
            professione.save()

            logger.info('Creata professione {}'.format(professione))
        else:
            professione = cd['professione']

        if cd['no_specializzazione']:
            logger.info('Specializzazione campo libero')
            specializzazione = TitoloSpecializzazione(
                nome=cd['nuova_specializzazione'].capitalize(),
                titolo=professione
            )
            specializzazione.save()
            logger.info('Creata specializzazione {}'.format(specializzazione))
        else:
            specializzazione = cd['specializzazione']

        if cd['no_skill']:
            skills = list(cd['skill'])

            nuove_skills = cd['nuova_skill']

            for skill in nuove_skills.split(','):
                skill_n = TitoloSkill(
                    nome=skill.capitalize(),
                    titolo=professione
                )
                skill_n.save()
                skills.append(skill_n)

        else:
            skills = cd['skill']

        titolo_personale = TitoloPersonale(
            persona=me,
            titolo=professione,
            specializzazione=specializzazione,
            data_ottenimento=cd['data_ottenimento'],
            data_scadenza=cd['data_scadenza'],
            attestato_file=cd['attestato_file'],
            codice_albo=cd['codice_albo'],
            esperienza=cd['esperienza']
        )
        titolo_personale.save()
        for skill in skills:
            titolo_personale.skills.add(skill)

        titolo_personale.save()
        logger.info('Creato Titolo Personale {}'.format(titolo_personale))

    else:
        logger.info('form non valido {}'.format(form.error))

    return redirect_url
