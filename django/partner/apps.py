from django.apps import AppConfig


class PartnerConfig(AppConfig):
    name = 'partner'

    def ready(self):
        from common import receivers