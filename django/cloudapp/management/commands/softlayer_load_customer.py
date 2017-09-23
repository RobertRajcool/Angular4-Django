from django.core.management import BaseCommand,CommandError
import SoftLayer
from django.conf import settings
class Command(BaseCommand):
    help = "This command Load the All Customers"
    redington_client = SoftLayer.Client(username=settings.SOFTLAYER_MASTER_USERNAME, api_key=settings.SOFTLAYER_MASTER_APIKEY)
    vendor_object = object
    master_brand_id = 0
    def handle(self, *args, **options):
        brand_details = self.redington_client['Account'].getOwnedBrands()
        self.master_brand_id = brand_details[0]['id']
        accounts = self.redington_client['Brand'].getAllOwnedAccounts(id=self.master_brand_id)
        for account in accounts:
            print(account['companyName']+'-'+str(account['id']))
        self.stdout.write(self.style.SUCCESS('Successfully SoftLayer Customers Loaded'))
    def create_customer_portal(self):
        return True