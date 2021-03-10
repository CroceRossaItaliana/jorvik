from rest_framework import serializers

from anagrafica.costanti import ESTENSIONE
from anagrafica.models import Persona, Appartenenza, Sede
from curriculum.serializers import TitoloSerializer


class SediSottostantiSerializer(serializers.ModelSerializer):
    id_comitato = serializers.SerializerMethodField('get_id')
    estensione = serializers.SerializerMethodField()

    def get_estensione(self, instance):
        return dict(ESTENSIONE)[instance.estensione]

    def get_id(self, instance):
        return instance.signature

    class Meta:
        model = Sede
        fields = ['id_comitato', 'nome', 'estensione', ]


class ComitatoSerializer(serializers.ModelSerializer):
    id_comitato = serializers.SerializerMethodField('get_id')
    estensione = serializers.SerializerMethodField()
    comitati_ids = serializers.ListField()
    comitati = SediSottostantiSerializer(read_only=True, many=True)

    def get_estensione(self, instance):
        return dict(ESTENSIONE)[instance.estensione]

    def get_id(self, instance):
        return instance.signature

    class Meta:
        model = Sede
        fields = ['id_comitato', 'nome', 'estensione', 'comitati_ids', 'comitati']


class SedeSerializer(serializers.ModelSerializer):
    id_comitato = serializers.SerializerMethodField('get_id')

    def get_estensione(self, instance):
        return dict(ESTENSIONE)[instance.estensione]

    def get_id(self, instance):
        return instance.signature

    class Meta:
        model = Sede
        fields = ['id_comitato', 'nome', ]


class AppartenenzaSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField('get_membro')
    sede = SedeSerializer()
    data_inizio = serializers.SerializerMethodField('get_inizio')
    data_fine = serializers.SerializerMethodField('get_fine')

    def get_inizio(self, instance):
        return str(instance.inizio)

    def get_fine(self, instance):
        return str(instance.fine)

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
    id_persona = serializers.SerializerMethodField('get_id')
    appartenenza_cm = serializers.SerializerMethodField('get_cm')
    appartenenza_iv = serializers.SerializerMethodField('get_iv')

    def get_cm(self, instance):
        return instance.cm

    def get_iv(self, instance):
        return instance.iv

    def get_id(self, instance):
        return instance.signature

    class Meta:
        model = Persona
        fields = [
            'id_persona', 'nome', 'cognome', 'codice_fiscale', 'data_nascita', 'comune_nascita',
            'provincia_nascita', 'stato_nascita', 'email_contatto', 'email_utenza', 'comune_residenza',
            'provincia_residenza', 'appartenenza_cm', 'appartenenza_iv',
        ]
