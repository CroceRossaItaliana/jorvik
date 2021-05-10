from django.apps import AppConfig


class AnagraficaConfig(AppConfig):
    name = 'anagrafica'

    def ready(self):
        import anagrafica.signals
