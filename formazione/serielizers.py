from rest_framework import serializers

from formazione.models import CorsoBase


class CorsoBaseSerializer(serializers.ModelSerializer):
    nome = serializers.SlugRelatedField(source='titolo', read_only=True, slug_field='nome')
    tipo = serializers.SlugRelatedField(source='titolo', read_only=True, slug_field='tipo')

    class Meta:
        model = CorsoBase
        fields = [
            'nome', 'tipo', 'data_ottenimento', 'data_scadenza'
        ]
