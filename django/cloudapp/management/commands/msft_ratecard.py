from django.core.management import BaseCommand
from background_scripts.microsoft.rate_card import RateCard

class Command(BaseCommand):
    help = "This command will fetch the MSFT Rate Card for Azure and Store in DB"

    def handle(self, *args, **kwargs):
        print("About to start loading RateCard")
        r = RateCard()
        r.storeRateCard()
        print("Loaded RateCard Data")