from django.core.management import BaseCommand
import requests
import datetime
from cloudapp.defaults import AppDefaults
from products.models import VendorDetails, Products
from users.models import RedUser
from django.utils import timezone


class Command(BaseCommand):
    help = "This command will load initial data into database"

    def add_arguments(self, parser):
        parser.add_argument('-t', '--target', type=str, nargs='?',
                            default=None,
                            help='Data loading target (aws_so_codes)'
                            )

    def handle(self, *args, **options):
        if not options.get('target', None):
            print("\033[0;37;41mPlease specify the target to load data.. \033[0m")
            return False

        if options['target'] == "aws_so_codes":
            self.load_aws_so_codes()
        elif options['target'] == "azure_so_codes":
            self.load_azure_so_codes()
        else:
            print("\033[0;37;41mInvalid option.. \033[0m")

    def load_aws_so_codes(self):
        vendor = VendorDetails.objects.filter(
            vendor_name=AppDefaults.cloud_vendor_codes(return_as='name', query_str='AWS')).first()
        user = RedUser.objects.filter(is_superuser=True).first()

        for code in AppDefaults.aws_jba_codes():
            data = {
                "product_name": code[1],
                "product_description": "Uses for SO generation",
                "vendor_details": vendor,
                "unit_cost": 0,
                "unit_price": 0,
                "standard_discount": 0,
                "product_status": 1,
                "product_featured": False,
                "product_billing_type": "Consumption",
                "product_jbacode": code[0],
                "product_created_by": user,
                "product_modified_by": user,
                "product_created_date": timezone.now(),
                "product_modified_date": timezone.now(),
                "product_currency": 1
            }

            if Products.objects.filter(product_name=code[1]).exists():
                product = Products.objects.filter(product_name=code[1]).first()
                product.__dict__.update(**data)
                product.save()
                print("Updated %s - %s" % (code[0], code[1]))
            else:
                Products.objects.create(**data)
                print("Loaded %s - %s" % (code[0], code[1]))

    def load_azure_so_codes(self):
        vendor = VendorDetails.objects.filter(
            vendor_name=AppDefaults.cloud_vendor_codes(return_as='name', query_str='MS')).first()
        user = RedUser.objects.filter(is_superuser=True).first()

        for code in AppDefaults.azure_jba_codes():
            data = {
                "product_name": code[1],
                "product_description": "Uses for SO generation",
                "vendor_details": vendor,
                "unit_cost": 0,
                "unit_price": 0,
                "standard_discount": 0,
                "product_status": 1,
                "product_featured": False,
                "product_billing_type": "Consumption",
                "product_jbacode": code[0],
                "product_created_by": user,
                "product_modified_by": user,
                "product_created_date": timezone.now(),
                "product_modified_date": timezone.now(),
                "product_currency": 1
            }

            if Products.objects.filter(product_name=code[1]).exists():
                product = Products.objects.filter(product_name=code[1]).first()
                product.__dict__.update(**data)
                product.save()
                print("Updated %s - %s" % (code[0], code[1]))
            else:
                Products.objects.create(**data)
                print("Loaded %s - %s" % (code[0], code[1]))
