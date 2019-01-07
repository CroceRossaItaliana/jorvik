from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Max
from django.template import Library
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from jorvik.settings import GOOGLE_KEY
from anagrafica.models import Persona, Delega
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.costanti import PERMESSI_TESTO, NESSUNO
from base.geo import ConGeolocalizzazione
from base.stringhe import genera_uuid_casuale
from base.tratti import ConDelegati
from base.utils import testo_euro
from ufficio_soci.elenchi import Elenco
from anagrafica.permessi.applicazioni import PRESIDENTE

register = Library()

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
def localizzatore(context, oggetto_localizzatore=None, continua_url=None, solo_italia=False):

    if not isinstance(oggetto_localizzatore, ConGeolocalizzazione):
        raise ValueError("Il tag localizzatore puo' solo essere usato con un oggetto ConGeolocalizzazione, ma e' stato usato con un oggetto %s." % (oggetto_localizzatore.__class__.__name__,))

    oggetto_tipo = ContentType.objects.get_for_model(oggetto_localizzatore)

    context.request.session['app_label'] = oggetto_tipo.app_label
    context.request.session['model'] = oggetto_tipo.model
    context.request.session['pk'] = oggetto_localizzatore.pk
    context.request.session['continua_url'] = continua_url

    url = "/geo/localizzatore/"
    if solo_italia:
        url += '?italia=1'
    context.update({
        'iframe_url': url,
    })
    return render_to_string('base_iframe_4_3.html', context)


@register.simple_tag(takes_context=True)
def delegati(context, delega=UFFICIO_SOCI, oggetto=None, continua_url=None, almeno=0):
    if not isinstance(oggetto, ConDelegati):
        raise ValueError("Il tag delegati puo' solo essere usato con un oggetto ConDelegati, ma e' stato usato con un oggetto %s." % (oggetto_localizzatore.__class__.__name__,))

    oggetto_tipo = ContentType.objects.get_for_model(oggetto)
    context.request.session['app_label'] = oggetto_tipo.app_label
    context.request.session['model'] = oggetto_tipo.model
    context.request.session['pk'] = oggetto.pk
    context.request.session['continua_url'] = continua_url
    context.request.session['delega'] = delega
    context.request.session['almeno'] = almeno
    url = "/strumenti/delegati/"
    context.update({
        'iframe_url': url,
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

    solo_deleghe_attive = deleghe == "solo_attive"
    almeno = context.request.me.permessi_almeno(oggetto, minimo_int,
                                                solo_deleghe_attive=solo_deleghe_attive)

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
    return range(number-meno)


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

