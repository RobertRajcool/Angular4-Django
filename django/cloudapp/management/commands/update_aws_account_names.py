from django.core.management import BaseCommand
from customers.models import CloudAccounts
import csv
import os


class Command(BaseCommand):
    help = 'Updates the AWS customer\'s linked account names from given file'

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, nargs='?',
                            help='csv file containing linked_account_ids & their account names')

    def handle(self, *args, **options):

        if not options['file']:
            raise ValueError('No file provided: Please provide a file, containing linked_account_ids & account_names')

        if os.path.splitext(options['file'])[-1:][0] != '.csv':
            raise ValueError('Invalid file format: Please provide a CSV file')

        file = open(options['file'], 'r')

        dict_reader = csv.DictReader(file)

        for record in dict_reader:
            cloud_account = CloudAccounts.objects.filter(type='AWS',
                                                         details__account_id=record['linked_account_id'])

            if not cloud_account.exists():
                print('No cloud Account found for [', record['linked_account_id'], ',', record['account_name'], ']')
                pass
            else:

                cloud_account = cloud_account.first()
                cloud_account.details.update({
                    'account_name': record['account_name']
                })
                cloud_account.save()

                print('Account Name updated for [', record['linked_account_id'], record['account_name'], ']')

        file.close()
