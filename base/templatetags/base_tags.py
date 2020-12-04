from os import path
from datetime import datetime
from django import template
from django.contrib.messages import constants
from django.utils.six import string_types
from anagrafica.permessi.costanti import PRESIDENTE, COMMISSARIO

register = template.Library()


@register.filter
def bool(value):
    if value:
        return 'true'
    else:
        return 'false'


@register.simple_tag(takes_context=True)
def show_test_users_with_credentials(context):
    from anagrafica.models import Persona
    from django.utils.safestring import mark_safe

    try:
        request = context['request']
        host = request.build_absolute_uri()

        if "provami.gaia.cri.it" in host or "127.0.0.1" in host:
            html = ''

            for delega_tipo in ['volontario_', 'presidente_',
                                'responsabile_formazione_',
                                'direttore_corso_', 'delegato_obiettivo_']:
                persona = Persona.objects.filter(nome__istartswith=delega_tipo).last()
                if persona:
                    html += "<div>%s : %s</div>" % (persona.utenza,
                                                    persona.utenza.check_password(persona.utenza.email))

            return mark_safe(html)
    except:
        # per escludere qualsiasi exception
        pass

    return ""


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, string_types):
        return text.startswith(starts)
    return False


@register.filter('level_to_bootstrap')
def level_to_bootstrap(message):
    map = {
        constants.DEBUG: 'alert-info',
        constants.INFO: 'alert-info',
        constants.SUCCESS: 'alert-success',
        constants.WARNING: 'alert-warning',
        constants.ERROR: 'alert-danger',
    }
    return map.get(message.level, 'alert-info')


@register.filter
def select_nomina_presidenziale(sede):
    delega_presidenziale= sede.deleghe_attuali(
        al_giorno=datetime.now(), tipo=PRESIDENTE, fine=None
    ).first()

    if delega_presidenziale:
        return 'Presidente'

    delega_presidenziale = sede.deleghe_attuali(
        al_giorno=datetime.now(), tipo=COMMISSARIO, fine=None
    ).first()

    if delega_presidenziale:
        return 'Commissario'
    # Caso in cui non ci sono delegati
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_url_for_staticfiles(context):
    """ Questa funzione serve per avere url del host attuale perchè per la
        renderizzazione del pdf server il percorso assoluto (con dominio)

        - In produzione non restituire nulla perchè {% static %} restituirà percorso corretto
            - (STATIC_URL in config/media.cnf)
        - Per gli ambienti di sviluppo o su staging gli statici hanno staticfiles folder diverso
            - Docker (/tmp/media)
            - Staging (STATIC_URL; o STATIC_URL to datafiles2)
    """
    from jorvik.settings import STATIC_URL

    if STATIC_URL.startswith('http'):
        return ''

    # request in context è passato nei metodi <genera_*> (pdf/verbale/attestato)
    request = context.get('request')
    if request:
        protocol = "http" if request.is_secure else 'https'
        return "%s://%s" % (protocol, request.get_host())

    return ''


@register.simple_tag
def get_filename(file):
    return path.basename(file.name)


@register.simple_tag(takes_context=True)
def richiesta_autorizzazione_button(context, action):
    richiesta = context['richiesta']
    oggetto = richiesta.oggetto

    display = True
    if hasattr(oggetto, 'qualifica_regresso') and oggetto.qualifica_regresso == True:
        display = False

    if action == 'nega':
        return display

    return True


@register.simple_tag(takes_context=True)
def richiesta_autorizzazione_button_text(context):
    richiesta = context['richiesta']

    if str(richiesta.oggetto_tipo) == 'Titolo personale':
        return 'Presa visione'
    return "Conferma"


@register.simple_tag(takes_context=True)
def add_flag_to_profile_url(context):
    elenco = context['elenco']
    elenco_short_name = elenco.SHORT_NAME if hasattr(elenco, 'SHORT_NAME') else ''
    return elenco_short_name

