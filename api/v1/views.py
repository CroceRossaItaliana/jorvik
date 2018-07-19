from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from oauth2_provider.ext.rest_framework import TokenHasScope
from api.settings import SCOPE_ANAGRAFICA_LETTURA_BASE, SCOPE_ANAGRAFICA_LETTURA_COMPLETA, SCOPE_APPARTENENZE_LETTURA

from api.v1 import serializzatori


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
