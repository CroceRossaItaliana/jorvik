from rest_framework import serializers

from anagrafica.models import Persona


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'nome', 'cognome', 'codice_fiscale']
