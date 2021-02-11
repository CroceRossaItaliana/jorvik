from rest_framework import serializers

from curriculum.models import TitoloPersonale


class TitoliCRISerializer(serializers.ModelSerializer):
    nome = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='nome')
    tipo = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='tipo')

    class Meta:
        model = TitoloPersonale
        fields = ['nome', 'tipo', 'data_ottenimento', 'data_scadenza']


class TitoliStudioSerializer(serializers.ModelSerializer):
    nome = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='nome')
    tipo = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='tipo')
    area = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='area')

    class Meta:
        model = TitoloPersonale
        fields = ['nome', 'tipo', 'area', 'data_ottenimento']


# class CompetenzeSerializer(serializers.ModelSerializer):
#     nome = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='nome')
#     tipo = serializers.SlugRelatedField(source='titolo', read_only='True', slug_field='tipo')
#
#     class Meta:
#         model = TitoloPersonale
#         fields = ['nome', 'tipo', 'data_ottenimento', 'data_scadenza']
