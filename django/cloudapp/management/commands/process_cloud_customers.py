from django.core.management import BaseCommand
import sys
from cloudapp.defaults import AppDefaults
from customers.models import CloudAccounts
from partner.models import Partner
from cloudtemplates.tasks import get_metrics, update_aws_details

class Command(BaseCommand):
    help = "This command will process various activities for cloud customers, spinning one process for each partner"

    def add_arguments(self, parser):
        parser.add_argument('type', type=str)
        parser.add_argument('vendor', type=str)

    def handle(self, *args, **options):
        type_of_operation = options['type']
        if not type_of_operation:
            print("Need type of operation")
            sys.exit(-1)

        vendor = options['vendor']
        if vendor != 'ALL' and not AppDefaults.cloud_vendor_codes(return_as='code', query_str=vendor):
            print("Vendor should either be ALL to process all types or individual ones to access just that cloud vendor")
            sys.exit(-2)

        vendor_ids = {
            'AWS': 1,
            'SoftLayer': 2,
            'MS': 3
        }

        partners = []
        if vendor == 'ALL':
            partners = Partner.objects.filter(id__in=(CloudAccounts.objects.filter(active=1) \
                .values('customer__partner').distinct()))
        else:
            partners = Partner.objects.filter(id__in=(CloudAccounts.objects.filter(vendor_id=vendor_ids[vendor], active=1) \
                .values('customer__partner').distinct()))

        if (type_of_operation == 'instance_details'):

            print("About to call update_aws_details for partners, Total count: %d " % (partners.count()))
            for partner in partners:
                print("Calling update_aws_details for Partner: %s " % (partner.pk,))
                update_aws_details.apply_async(args=[partner.pk])
        elif (type_of_operation == 'instance_metrics'):

            print("About to call get_metrics for partners, Total count: %d " %(partners.count()))
            for partner in partners:
                print("Calling get_metrics for Partner: %s " %(partner.pk,))
                get_metrics.apply_async(args=[partner.pk])



