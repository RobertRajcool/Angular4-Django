from django.core.management import BaseCommand
from background_scripts.microsoft.get_utilization import UtilizationRecords
from datetime import datetime

class Command(BaseCommand):
    help = "This command will fetch the MSFT Azure Utilization for a Partner and/or Customer"

    def add_arguments(self, parser):
        #parser.add_argument('partner_id', nargs='+', type=int)
        #parser.add_argument('customer_id', nargs='*', type=int)
        parser.add_argument('tenant_id', type=str)
        parser.add_argument('subscription_id', type=str)
        parser.add_argument('fromdate', type=str)
        parser.add_argument('todate', type=str)

    def handle(self, *args, **options):
        print("About to start fetching utilization")
        util = UtilizationRecords(options['tenant_id'],
                                  options['subscription_id'],
                                  options['fromdate'],
                                  options['todate'])
        util.getUtilization()
        print("Fetched Util Data")