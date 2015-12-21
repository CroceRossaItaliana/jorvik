from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.template import Library
from django.template.loader import render_to_string

from anagrafica.models import Persona
from anagrafica.permessi.applicazioni import UFFICIO_SOCI
from anagrafica.permessi.costanti import PERMESSI_TESTO, NESSUNO
from base.geo import ConGeolocalizzazione
from base.stringhe import genera_uuid_casuale
from base.tratti import ConDelegati
from ufficio_soci.elenchi import Elenco

register = Library()


@register.simple_tag(takes_context=True)
def card(context, persona=None, nome=True, extra_class="btn btn-sm btn-default", avatar=False):

    if not isinstance(persona, Persona):
        raise ValueError("Il tag card puo' solo essere usato con una persona, ma e' stato usato con un oggetto %s." % (persona.__class__.__name__,))

    context.update({
        'card_persona': persona,
        'card_nome': nome,
        'card_avatar': avatar,
        'card_class': extra_class,
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


@register.simple_tag(takes_context=True)
def localizzatore(context, oggetto_localizzatore=None, continua_url=None):

    if not isinstance(oggetto_localizzatore, ConGeolocalizzazione):
        raise ValueError("Il tag localizzatore puo' solo essere usato con un oggetto ConGeolocalizzazione, ma e' stato usato con un oggetto %s." % (oggetto_localizzatore.__class__.__name__,))

    oggetto_tipo = ContentType.objects.get_for_model(oggetto_localizzatore)

    context.request.session['app_label'] = oggetto_tipo.app_label
    context.request.session['model'] = oggetto_tipo.model
    context.request.session['pk'] = oggetto_localizzatore.pk
    context.request.session['continua_url'] = continua_url

    url = "/geo/localizzatore/"
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
def permessi_almeno(context, oggetto, minimo="lettura"):
    """
    Controlla che l'utente attuale -estrapolato dal contesto- abbia i permessi
     minimi su un determinato oggetto. Ritorna True o False.
    """

    if minimo not in PERMESSI_TESTO:
        raise ValueError("Permesso '%s' non riconosciuto. Deve essere in 'PERMESSI_TESTO'." % (minimo,))

    minimo_int = PERMESSI_TESTO[minimo]

    if minimo_int == NESSUNO:
        return True

    if not hasattr(context.request, 'me'):
        return False

    almeno = context.request.me.permessi_almeno(oggetto, minimo_int)
    return almeno


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
        """

        i = 0
        for elemento in elementi:
            if not elemento.locazione:
                continue  # Salta elementi senza posizione.

            context.update({"elemento": elemento})
            contenuto = str(self.nodelist.render(context)).strip().replace("\n", " ")
            colore = str(self.nodelist_icona.render(context)).strip().replace("\n", " ")

            output += """
            messaggio.push(new google.maps.InfoWindow({
                content: \"""" + contenuto + """\"
            }));
            marcatore.push(new google.maps.Marker({
                position: new google.maps.LatLng(""" + str(elemento.locazione.geo.y) + """, """ + str(elemento.locazione.geo.x) + """),
                map: map, animation: google.maps.Animation.DROP, icon: 'https://maps.google.com/mapfiles/ms/icons/""" + colore + """-dot.png'
            }));
            google.maps.event.addListener(marcatore[""" + str(i) + """], 'click', function() {
                messaggio[""" + str(i) + """].open(map, marcatore[""" + str(i) + """]);
            });
            """
            i += 1

        output += """
            }
            function loadScript() {
              var script = document.createElement("script");
              script.type = "text/javascript";
              script.src = "https://maps.google.com/maps/api/js?sensor=false&callback=initialize";
              document.body.appendChild(script);
          }
          window.onload = loadScript;
        </script>
        """

        return output

