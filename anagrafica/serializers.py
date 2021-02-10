from rest_framework import serializers

from anagrafica.models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    my_field = serializers.SerializerMethodField('id_hash')

    def id_hash(self, instance):
        return hash(instance.codice_fiscale)

    class Meta:
        model = Persona
        fields = ['id', 'nome', 'cognome', 'codice_fiscale', 'my_field']
