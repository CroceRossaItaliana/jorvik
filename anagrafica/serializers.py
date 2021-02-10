import hashlib

from rest_framework import serializers

from anagrafica.models import Persona, Appartenenza


class AppartenenzaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appartenenza
        fields = ['inizio', 'fine', 'sede', 'membro']


class PersonaSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_id_hash')
    id_persona = serializers.SerializerMethodField('get_id')
    appartenenze = AppartenenzaSerializer(read_only=True, many=True)

    def get_id(self, instance):
        return instance.id

    def get_id_hash(self, instance):
        return hashlib.sha1(instance.codice_fiscale.encode('utf-8')).hexdigest()

    class Meta:
        model = Persona
        fields = ['id', 'id_persona', 'nome', 'cognome', 'codice_fiscale', 'appartenenze']
