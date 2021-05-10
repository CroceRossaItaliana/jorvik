from rest_framework import serializers

from formazione.models import CorsoBase, LezioneCorsoBase


class LezioneCorsoBaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = LezioneCorsoBase
        fields = [
            'nome',
        ]


class CorsoBaseSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('get_signature')
    id_corso = serializers.SerializerMethodField('get_id')
    nome = serializers.SlugRelatedField(source='titolo_cri', read_only=True, slug_field='nome')
    direttore = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    lezioni = LezioneCorsoBaseSerializer(many=True, read_only=True)

    def get_id(self, instance):
        return instance.id

    def get_signature(self, instance):
        return str(instance.signature)

    def get_direttore(self, instance):
        return instance.direttori_corso(as_delega=True).first().persona.nome_completo

    def get_tipo(self, instance):
        return dict(CorsoBase.TIPO_CHOICES)[instance.tipo]

    class Meta:
        model = CorsoBase
        fields = [
            'id', 'id_corso', 'nome', 'tipo', 'data_esame', 'data_esame_2', 'data_esame_pratica', 'direttore', 'lezioni'
        ]
