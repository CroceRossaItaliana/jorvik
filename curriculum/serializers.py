from rest_framework import serializers

from curriculum.models import TitoloPersonale, Titolo


class TitoloSerializer(serializers.ModelSerializer):
    nome = serializers.SlugRelatedField(source='titolo', read_only=True, slug_field='nome')
    tipo = serializers.SerializerMethodField()

    def get_tipo(self, instance):
        return dict(Titolo.TIPO)[instance.titolo.tipo]

    class Meta:
        model = TitoloPersonale
        fields = ['nome', 'tipo', 'data_ottenimento', 'data_scadenza']
