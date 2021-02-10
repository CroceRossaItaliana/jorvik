import json

from anagrafica.models import Persona
from anagrafica.serializers import PersonaSerializer


def serializer_persona(idPersona):
    s_persona = PersonaSerializer(Persona.objects.get(pk=idPersona))
    print(json.dumps(s_persona.data))
