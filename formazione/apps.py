from django.apps import AppConfig


class FormazioneConfig(AppConfig):
    name = 'formazione'

    def ready(self):
        import formazione.signals
