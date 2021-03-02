import hashlib

from rest_framework import serializers

from anagrafica.models import Persona, Appartenenza, Sede
from curriculum.serializers import TitoloSerializer


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', ]


class AppartenenzaSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField('get_membro')
    # sede = SedeSerializer()
    data_inizio = serializers.SerializerMethodField('get_inizio')
    data_fine = serializers.SerializerMethodField('get_fine')

    def get_inizio(self, instance):
        return instance.inizio

    def get_fine(self, instance):
        return instance.fine

    def get_membro(self, instance):
        return dict(Appartenenza.MEMBRO)[instance.membro]

    class Meta:
        model = Appartenenza
        fields = ['sede', 'tipo', 'data_inizio', 'data_fine', ]


class CurriculumPersonaSerializer(serializers.ModelSerializer):
    id_persona = serializers.SerializerMethodField('get_id')
    appartenenze = AppartenenzaSerializer(read_only=True, many=True)
    titoli = TitoloSerializer(read_only=True, many=True)

    def get_id(self, instance):
        return instance.signature

    class Meta:
        model = Persona
        fields = ['id_persona', 'nome', 'cognome', 'codice_fiscale', 'appartenenze', 'titoli']


class PersonaSerializer(serializers.ModelSerializer):
    pass
