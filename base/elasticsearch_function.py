import json

from anagrafica.serializers import CurriculumPersonaSerializer


def serializer_persona(persona):
    s_persona = CurriculumPersonaSerializer(persona)
    print(json.dumps(s_persona.data))
