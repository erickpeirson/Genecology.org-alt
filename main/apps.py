from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        super(MainConfig, self).ready()