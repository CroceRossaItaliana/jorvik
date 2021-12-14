from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from oauth2_provider.ext.rest_framework import TokenHasScope
from api.settings import SCOPE_ANAGRAFICA_LETTURA_BASE, SCOPE_ANAGRAFICA_LETTURA_COMPLETA, SCOPE_APPARTENENZE_LETTURA

from api.v1 import serializzatori
from anagrafica.permessi.applicazioni import PERMESSI_NOMI_DICT

from anagrafica.models import Persona, Sede
from posta.models import Messaggio
import base64
from django.core.files.base import ContentFile


# /me/anagrafica/base/
class MiaAnagraficaBase(APIView):
    """
    Una vista che ritorna informazioni sulla persona identificata.
    """
    permission_classes = (permissions.IsAuthenticated,
                          TokenHasScope)
    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE]

    def get(self, request, format=None):
        dati = serializzatori.persona_anagrafica_base(request.user.persona)
        return Response(dati)


# /me/anagrafica/completa/
class MiaAnagraficaCompleta(APIView):
    """
    Una vista che ritorna l'anagrafica completa della persona identificata
     (anagrafica base, più dati aggiuntivi).
    """

    permission_classes = (permissions.IsAuthenticated,
                          TokenHasScope)
    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA]

    def get(self, request, format=None):
        dati = serializzatori.persona_anagrafica_completa(request.user.persona)
        return Response(dati)


# /me/appartenenze/attuali/
class MieAppartenenzeAttuali(APIView):
    """
    Una vista che ritorna informazioni sulle appartenenze attuali.
    """

    required_scopes = [SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        me = request.user.persona
        appartenenze = me.appartenenze_attuali()
        appartenenze = [serializzatori.appartenenza(i) for i in appartenenze]
        dati = {"appartenenze": appartenenze}
        return Response(dati)


def get_user_data(persona, filtered_for=None):
    # Persona
    dati = {
        'id_persona': persona.pk,
        'nome': persona.nome,
        'cognome': persona.cognome,
        'data_di_nascita': persona.data_nascita,
        'codice_fiscale': persona.codice_fiscale,
        'email_utente': persona.utenza and persona.utenza.email or None,
    }

    if persona.email is not None:
        dati['email'] = persona.email

    # Comitato
    deleghe = persona.deleghe_attuali()

    l_deleghe = []
    for delega in deleghe:
        estensione = None
        tipologia = None
        toAdd = True

        if (isinstance(delega.oggetto, Sede)):
            estensione = delega.oggetto.estensione
            tipologia = delega.oggetto.tipo

        d_delega = {
            'id': delega.id,
            'tipo': PERMESSI_NOMI_DICT[delega.tipo],
            'codice_tipo': delega.tipo,
            'appartenenza': delega.oggetto.nome,
            'appartenenza_pk': delega.oggetto.pk,
            'appartenenza_estensione': estensione,
            'appartenenza_tipologia': tipologia,
        }
        if filtered_for:
            oggetto_pk = filtered_for.get('oggetto_pk')
            deleghe = filtered_for.get('deleghe', [])

            if deleghe and delega.tipo not in deleghe:
                toAdd = False
            if oggetto_pk and oggetto_pk != delega.oggetto.pk:
                toAdd = False
            
        if toAdd:
            l_deleghe.append(d_delega)

    dati['deleghe'] = l_deleghe

    # appartenenze
    appartenenze = persona.appartenenze_attuali()
    l_appartenenza = []

    for appartenenza in appartenenze:
        comitato = appartenenza.sede
        l_appartenenza.append({
            'id': comitato.id,
            'nome': comitato.nome,
            'tipo': {
                'id': appartenenza.membro,
                'descrizione': appartenenza.get_membro_display()
            },
            'comitato': {
                'id': comitato.estensione,
                'descrizione': comitato.get_estensione_display()
            },
            'inizio': appartenenza.inizio.strftime("%Y-%m-%d")
        })
    dati['appartenenze'] = l_appartenenza

    return dati


class MiaAppartenenzaComplaeta(APIView):
    """
        ID utente, - Persona

        nome, - Persona

        cognome, - Persona

        indirizzo mail di contatto - Persona

        rispettiva sede di appartenenza, - Persona

        ID comitato,

        nome comitato,

        estensione del comitato R/P/L/T,

        delega
    """
    permission_classes = (permissions.IsAuthenticated,
                          TokenHasScope)
    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA,
                       SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        me = request.user.persona

        dati = get_user_data(me)
        return Response(dati)


# /user/anagrafica/base/
class UserAnagraficaBase(APIView):
    """
    Una vista che ritorna informazioni sulla persona passata in input.
    """

    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE]

    def get(self, request, format=None):
        userid = request.data.get('pk')
        dati = {}

        if userid:
            persona = Persona.objects.get(pk=userid)
            if persona:
                dati = serializzatori.persona_anagrafica_base(persona)

        return Response(dati)


# /user/anagrafica/completa/
class UserAnagraficaCompleta(APIView):
    """
    Una vista che ritorna l'anagrafica completa della persona passata in input.
     (anagrafica base, più dati aggiuntivi).
    """
    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA]

    def get(self, request, format=None):
        userid = request.data.get('pk')
        dati = {}

        if userid:
            persona = Persona.objects.get(pk=userid)
            if persona:
                dati = serializzatori.persona_anagrafica_completa(persona)

        return Response(dati)


# /user/appartenenze/attuali/
class UserAppartenenzeAttuali(APIView):
    """
    Una vista che ritorna informazioni sulle appartenenze attuali.
    """

    required_scopes = [SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        userid = request.data.get('pk')
        dati = {}

        if userid:
            persona = Persona.objects.get(pk=userid)
            if persona:
                appartenenze = persona.appartenenze_attuali()
                appartenenze = [serializzatori.appartenenza(i) for i in appartenenze]
                dati = {"appartenenze": appartenenze}

        return Response(dati)


def get_user_data_extended(persona, filtered_for=None):
    data = get_user_data(persona, filtered_for)
    data.update(serializzatori.persona_anagrafica_completa(persona))

    return data


class UserAppartenenzaCompleta(APIView):
    """
        ID utente, - Persona

        nome, - Persona

        cognome, - Persona

        indirizzo mail di contatto - Persona

        rispettiva sede di appartenenza, - Persona

        ID comitato,

        nome comitato,

        estensione del comitato R/P/L/T,

        delega
    """

    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA,
                       SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        userid = request.data.get('pk')
        dati = {}

        if userid:
            persona = Persona.objects.get(pk=userid)
            if persona:
                dati = get_user_data_extended(persona)

        return Response(dati)

#http://localhost:8000/api/v1/search/users/
class SearchUserAppartenenzaCompleta(APIView):
    """
    Una vista che ritorna una persona, o un lista di persone, in base ai criteri di ricerca
    """

    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA,
                       SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        nome = request.data.get('nome')
        cognome = request.data.get('cognome')
        codice_fiscale = request.data.get('codice_fiscale')
        data_nascita = request.data.get('data_nascita')
        sede_id = request.data.get('sede')
        dati = []

        if sede_id:
            qs=Sede.objects.get(pk=sede_id).membri_attuali(figli=True)
        else:
            qs= Persona.objects.all()

        if nome:
            qs=qs.filter(nome__icontains=nome)
        if cognome:
            qs=qs.filter(cognome__icontains=cognome)
        if codice_fiscale:
            qs=qs.filter(codice_fiscale__iexact=codice_fiscale)
        if data_nascita:
            qs=qs.filter(data_nascita=data_nascita)

        for persona in qs:
            dati.append(get_user_data_extended(persona))




        return Response(dati)


class SearchUserByDelegaAppartenenzaCompleta(APIView):
    """
    Una vista che ritorna una persona, o un lista di persone, in base ai criteri di ricerca
    """

    required_scopes = [SCOPE_ANAGRAFICA_LETTURA_BASE,
                       SCOPE_ANAGRAFICA_LETTURA_COMPLETA,
                       SCOPE_APPARTENENZE_LETTURA]

    def get(self, request, format=None):
        deleghe = request.data.get('deleghe')
        soggetto = request.data.get('soggetto')
        sede_livello = request.data.get('sede_livello')
        
        added = []
        dati = []

        if soggetto:
            persona = Persona.objects.get(pk=soggetto)

            sede = persona.sede_riferimento()

            if sede_livello == 'R':
                sede = sede.sede_regionale
            
            if sede_livello == 'N':
                sede = Sede.objects.get(pk=1)

            for d in deleghe:
                for p in sede.delegati_attuali(tipo=d, solo_deleghe_attive=True):
                    if p.pk not in added:
                        dati.append(get_user_data_extended(p, filtered_for={
                            'oggetto_pk': sede.pk,
                            'deleghe': deleghe,
                        }))
                        added.append(p.pk)

        return Response(dati)


class SendMessage(APIView):
    """
    Invia un messaggio di posta
    """

    def post(self, request, format=None):
        modello = request.data.get('modello')
        oggetto = request.data.get('oggetto')
        corpo = request.data.get('corpo')
        mittente_pk = request.data.get('mittente')
        destinatari_pk = request.data.get('destinatari')
        allegati_b64 = request.data.get('allegati')
        
        mittente = None
        destinatari = []
        allegati = []

        if mittente_pk:
            mittente = Persona.objects.get(pk=mittente_pk)
        if destinatari_pk:
            destinatari = Persona.objects.filter(pk__in=destinatari_pk).all()
        
        if mittente and destinatari:
            Messaggio.costruisci_e_accoda(
                oggetto=oggetto,
                modello="email_benemerenza_notifica.html",
                corpo={
                    'testo': corpo
                },
                mittente=mittente,
                destinatari=destinatari
            )

        return Response()
        



# serializzatori._campo(comitato.estensione, comitato.get_estensione_display())
