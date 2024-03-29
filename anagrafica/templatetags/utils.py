from datetime import timezone, datetime

from django import template
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Max
from django.template import Library
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from formazione.forms import ModuloCreaOperatoreSala
from jorvik import settings
from jorvik.settings import GOOGLE_KEY
from ..models import Persona, Delega
from ..permessi.applicazioni import PRESIDENTE
from ..permessi.applicazioni import UFFICIO_SOCI
from ..permessi.costanti import PERMESSI_TESTO, NESSUNO
from base.geo import ConGeolocalizzazione
from base.stringhe import genera_uuid_casuale
from base.tratti import ConDelegati
from base.utils import testo_euro
from ufficio_soci.elenchi import Elenco
from anagrafica.permessi.applicazioni import PERMESSI_NOMI_DICT

register = Library()


@register.filter
def partecipazione_riunione(persona):

    start_date = datetime.strptime(settings.INIZIO_ASSEMBLEA_NAZIONALE, '%m/%d/%Y %H:%M:%S')
    finish_date = datetime.strptime(settings.FINE_ASSEMBLEA_NAZIONALE, '%m/%d/%Y %H:%M:%S')

    return persona.utenza.groups.filter(name='Assemblea').exists() and start_date < datetime.now() < finish_date


@register.filter
def partecipazione_riunione_consiglieri(persona):
    start_date = datetime.strptime(settings.INIZIO_ASSEMBLEA_NAZIONALE_COMMISSARI, '%m/%d/%Y %H:%M:%S')
    finish_date = datetime.strptime(settings.FINE_ASSEMBLEA_NAZIONALE_COMMISSARI, '%m/%d/%Y %H:%M:%S')

    return persona.utenza.groups.filter(name='Assemblea giovani').exists() and start_date < datetime.now() < finish_date


@register.filter
def partecipazione_riunione_volontari(persona):
    start_date = datetime.strptime(settings.INIZIO_ASSEMBLEA_MATERA_VOLONTARI, '%m/%d/%Y %H:%M:%S')
    finish_date = datetime.strptime(settings.FINE_ASSEMBLEA_MATERA_VOLONTARI, '%m/%d/%Y %H:%M:%S')

    return persona.utenza.groups.filter(name='Assemblea di Matera').exists() and start_date < datetime.now() < finish_date

@register.filter
def tipo_delega(tipo):
    return dict(ModuloCreaOperatoreSala.NOMINA)[tipo]

@register.filter
def stato_riserva(riserva):
    ATTUALE = 'Attuale'
    PASSATA = 'Passata'
    # Se la riserva non è iniziata ne passata allora non mostriamo niente fino alla sua attivazione
    NON_ATTIVA = ''

    oggi = timezone.now()

    # La riserva no ha una fine è in stato indeterminato
    if not riserva.fine:
        return ATTUALE

    # se il giorno odierno e compreso tra inizio e fine delle riserve, questa è attuale
    if riserva.inizio <= oggi <= riserva.fine:
        return ATTUALE
    # se il giorno odierno è maggiore della fine riserva, questa è passata
    elif oggi > riserva.fine:
        return PASSATA
    # se il giorno di inizio della riserva è maggiore del giorno odierno, questa non è ancora attiva
    elif riserva.inizio > oggi:
        return NON_ATTIVA


@register.filter
def select_presidente_commissario_da_persona(persona):
    return 'Presidente' if persona.deleghe_attuali(tipo=PRESIDENTE).exists() else 'Commissario'


@register.filter
def select_presidente_commisario_da_sede(sede):
    return 'Presidente' if sede.presidente() else 'Commissario'


@register.simple_tag(takes_context=True)
def card(context, persona=None, nome=True, extra_class="btn btn-sm btn-default", avatar=False, mute_contact=False):

    if not isinstance(persona, Persona):
        raise ValueError("Il tag card puo' solo essere usato con una persona, ma e' stato usato con un oggetto %s." % (persona.__class__.__name__,))

    context.update({
        'card_persona': persona,
        'card_nome': nome,
        'card_avatar': avatar,
        'card_class': extra_class,
        'mute_contact': mute_contact,
    })

    return render_to_string('anagrafica_tags_card.html', context)


@register.simple_tag(takes_context=True)
def elenco(context, oggetto_elenco=None,):

    if not isinstance(oggetto_elenco, Elenco):
        raise ValueError("Il tag elenco puo' solo essere usato con un oggetto Elenco, ma e' stato usato con un oggetto %s." % (oggetto_elenco.__class__.__name__,))

    elenco_id = genera_uuid_casuale()
    context.request.session["elenco_%s" % (elenco_id,)] = oggetto_elenco  # Passa elenco in sessione.

    context.update({
        'iframe_url': "/us/elenco/%s/1/" % (elenco_id,)
    })
    return render_to_string('us_elenchi_inc_iframe.html', context)


@register.simple_tag()
def checkbox(booleano, extra_classe='', con_testo=1):
    classe = "text-danger fa-square"
    testo = ""
    if booleano:
        classe = "text-success fa-check-square"
    if con_testo:
        testo = "<span class='text-success'>FATTO</span>" if booleano else \
            "<span class='text-danger'>DA FARE</span>"

    return mark_safe(" <i class='fa fa-fw %s %s'></i> %s" % (classe, extra_classe, testo))


@register.simple_tag(takes_context=True)
def reload_locazione(context):
    request = context.request
    locazione = context['locazione']

    if 'reload_locazione' in request.session:
        reload_locazione = request.session['reload_locazione']
        locazione_field, locazione_object = reload_locazione
        locazione = getattr(context['oggetto'], locazione_field)

        if locazione_field == 'sede_operativa':
            locazione = locazione_object
        del request.session['reload_locazione']

    return locazione


@register.simple_tag(takes_context=True)
def localizzatore(context,
                  oggetto_localizzatore=None,
                  continua_url=None,
                  solo_italia=False, **kwargs):

    if not isinstance(oggetto_localizzatore, ConGeolocalizzazione):
        raise ValueError("Il tag localizzatore puo' solo essere usato con un oggetto ConGeolocalizzazione, ma e' stato usato con un oggetto %s." % (oggetto_localizzatore.__class__.__name__,))

    oggetto_tipo = ContentType.objects.get_for_model(oggetto_localizzatore)

    context.request.session['app_label'] = oggetto_tipo.app_label
    context.request.session['model'] = oggetto_tipo.model
    context.request.session['pk'] = oggetto_localizzatore.pk
    context.request.session['continua_url'] = continua_url

    if 'modifica_indirizzo_sede' in context.request.session:
        del context.request.session['modifica_indirizzo_sede']

    # (GAIA-280) Modifica degli indirizzi dei campi aggiuntivi di una <Sede>
    modifica_indirizzo_sede = None
    if 'modifica_indirizzo_sede' in kwargs:
        modifica_indirizzo_sede = kwargs.pop('modifica_indirizzo_sede')

    if modifica_indirizzo_sede is not None:
        context.request.session['modifica_indirizzo_sede'] = modifica_indirizzo_sede

    url = reverse('geo_localizzatore')
    if solo_italia:
        url += '?italia=1'

    context.update({
        'iframe_url': url,
    })
    return render_to_string('base_iframe_4_3.html', context)


@register.simple_tag(takes_context=True)
def delegati(context, delega=UFFICIO_SOCI, oggetto=None, continua_url=None, almeno=0, *args, **kwargs):
    if not isinstance(oggetto, ConDelegati):
        msg = "Il tag delegati può solo essere usato con un oggetto ConDelegati, " \
              "ma è stato usato con un oggetto %s."
        raise ValueError(msg % oggetto_localizzatore.__class__.__name__)

    oggetto_tipo = ContentType.objects.get_for_model(oggetto)
    context.request.session['app_label'] = oggetto_tipo.app_label
    context.request.session['model'] = oggetto_tipo.model
    context.request.session['pk'] = oggetto.pk
    context.request.session['continua_url'] = continua_url
    context.request.session['delega'] = delega
    context.request.session['almeno'] = almeno
    context.update({
        'iframe_url': reverse('strumenti_delegati'),
    })
    return render_to_string('base_iframe_4_3.html', context)

@register.assignment_tag(takes_context=True)
def giorni_ore_minuti(context, tdelta):
    if not tdelta:
        return 0, 0, 0
    return tdelta.days, tdelta.seconds//3600, (tdelta.seconds//60)%60


@register.assignment_tag(takes_context=True)
def permessi_almeno(context, oggetto, minimo="lettura", deleghe="solo_attive"):
    """
    Controlla che l'utente attuale -estrapolato dal contesto- abbia i permessi
     minimi su un determinato oggetto. Ritorna True o False.
    """

    if deleghe not in ("solo_attive", "tutte"):
        raise ValueError("Valore per 'deleghe' non riconosciuto.")

    if minimo not in PERMESSI_TESTO:
        raise ValueError("Permesso '%s' non riconosciuto. Deve essere in 'PERMESSI_TESTO'." % (minimo,))

    minimo_int = PERMESSI_TESTO[minimo]

    if minimo_int == NESSUNO:
        return True

    if not hasattr(context.request, 'me'):
        return False

    me = context.request.me

    if not me:
        return False

    solo_deleghe_attive = deleghe == "solo_attive"
    almeno = me.permessi_almeno(oggetto, minimo_int, solo_deleghe_attive=solo_deleghe_attive)
    return almeno


@register.assignment_tag(takes_context=True)
def partecipazione(context, turno):
    """
    Controlla lo stato di partecipazione tra turno e attivita'.
    """

    if not hasattr(context.request, 'me'):
        return turno.TURNO_NON_PUOI_PARTECIPARE_ACCEDI

    return turno.persona(context.request.me)


@register.tag()
def mappa(parser, token):
    nodelist = parser.parse(('icona_colore', 'endmappa',))
    tag_name, elementi = token.split_contents()
    elementi = template.Variable(elementi)
    token = parser.next_token()
    nodelist_icona = None
    if token.contents == 'icona_colore':
        nodelist_icona = parser.parse(('endmappa',))
        token = parser.next_token()
    return NodoMappa(nodelist, nodelist_icona, elementi)


@register.simple_tag(takes_context=True)
def euro(context, numero):
    return mark_safe(testo_euro(numero, simbolo_html=True))


@register.simple_tag(takes_context=True)
def sede_delega(context, utente, deleghe):
    if deleghe:
        deleghe = utente.deleghe.filter(tipo__in=deleghe)
        return ','.join([force_text(sede) for sede in utente.sedi_deleghe_attuali(deleghe=deleghe)])
    return ''


@register.assignment_tag()
def livello_max(queryset):
    try:
        massimo = queryset.aggregate(num=Max('level'))
        return massimo['num']
    except:
        return 0


@register.simple_tag()
def differenza(a, b, piu=0):
    return a - b + piu


@register.filter(name='volte')
def volte(number, meno=0):
    try:
        return range(number-meno)
    except TypeError:
        pass


class NodoMappa(template.Node):
    def __init__(self, nodelist, nodelist_icona, elementi):
        self.nodelist = nodelist
        self.nodelist_icona = nodelist_icona
        self.elementi = elementi
    def render(self, context):
        elementi = self.elementi.resolve(context)
        if not isinstance(elementi, (QuerySet, list)):
            elementi = [elementi]
        output = """
        <div id="laMappa" class="col-md-12" style="min-height: 700px;">
        </div>
        <script type="text/javascript">
        function initialize() {
          var opzioni = {
            zoom: 6,
            center: new google.maps.LatLng(41.9,12.4833333),
            mapTypeId: google.maps.MapTypeId.ROADMAP
          }
          var map = new google.maps.Map(document.getElementById("laMappa"), opzioni);
          var messaggio = [], marcatore = [];
          var latlngbounds = new google.maps.LatLngBounds();
        """

        i = 0
        elementi_pieni = False
        for elemento in elementi:
            if not elemento.locazione:
                continue  # Salta elementi senza posizione.

            elementi_pieni = True

            context.update({"elemento": elemento})
            contenuto = str(self.nodelist.render(context)).strip().replace("\n", " ")
            colore = str(self.nodelist_icona.render(context)).strip().replace("\n", " ")

            output += """
            messaggio.push(new google.maps.InfoWindow({
                content: \"""" + contenuto + """\"
            }));
            var latlng = new google.maps.LatLng(""" + str(elemento.locazione.geo.y) + """, """ + str(elemento.locazione.geo.x) + """);
            latlngbounds.extend(latlng);
            marcatore.push(new google.maps.Marker({
                position: latlng,
                map: map, animation: google.maps.Animation.DROP, icon: 'https://maps.google.com/mapfiles/ms/icons/""" + colore + """-dot.png'
            }));
            google.maps.event.addListener(marcatore[""" + str(i) + """], 'click', function() {
                messaggio[""" + str(i) + """].open(map, marcatore[""" + str(i) + """]);
            });
            """
            i += 1
        if not elementi_pieni:
            return ''

        output += """
            map.setCenter(latlngbounds.getCenter());
            map.fitBounds(latlngbounds);

            }
            function loadScript() {
              var script = document.createElement("script");
              script.type = "text/javascript";
              script.src = "https://maps.googleapis.com/maps/api/js?sensor=false&callback=initialize&key=""" + GOOGLE_KEY + """ ";
              document.body.appendChild(script);
          }
          window.onload = loadScript;
        </script>
        """

        return output


@register.simple_tag()
def image_as_base64(image_file):
    import os
    import base64
    import pathlib

    image_path = image_file.path

    if not os.path.isfile(image_path):
        return None

    encoded_string = ''
    extension = pathlib.Path(image_path).suffix

    with open(image_path, 'rb') as img:
        encoded_string = base64.b64encode(img.read())

    return 'data:image/%s;base64,%s' % (extension, encoded_string.decode("utf-8"))


@register.simple_tag(takes_context=True)
def get_top_navbar(context):
    from django.contrib.auth.models import AnonymousUser

    # menu_applicazioni passato nel context nei deocratori in: autenticazione.funzioni

    request = context['request']
    user = request.user

    menu = context.get('menu_applicazioni')
    if menu:
        return menu

    if user and not isinstance(user, AnonymousUser):
        # restituisci il menu chiamando il metodo direttamente
        return user.applicazioni_disponibili

    return ""


@register.filter
def is_rifiutato(id):
    from ufficio_soci.models import Tesserino
    return False if Tesserino.objects.filter(persona=id, stato_richiesta=Tesserino.RIFIUTATO).count() else True


@register.simple_tag(takes_context=True)
def add_session_flag_to_profile_urls(context):
    request = context['request']

    if 'us' in request.session.keys():
        return '?us'
    elif 'ea' in request.session.keys():
        return '?ea'
    return ''
