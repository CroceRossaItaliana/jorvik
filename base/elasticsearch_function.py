import json

from anagrafica.serializers import PersonaSerializer


def serializer_persona(persona):
    s_persona = PersonaSerializer(persona)
    print(json.dumps(s_persona.data))
