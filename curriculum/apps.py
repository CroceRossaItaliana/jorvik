from django.apps import AppConfig


class CurriculumConfig(AppConfig):
    name = 'curriculum'

    def ready(self):
        import curriculum.signals
