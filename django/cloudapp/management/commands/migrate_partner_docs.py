import os
import csv
from redington import settings
from django.core.management import BaseCommand
from django.utils.crypto import get_random_string
from partner.models import InitialPartner, InitialContactDetails, InitialDocumentDetails

PARTNER_TYPE = ['Reseller', 'Consulting & Implementation', 'Managed Service Provider', 'Technology Partner']
CONTACT_TYPE = ['P', 'D/O', 'A&O', 'S']
DOCS_TYPES = {
    'Copy of Passport - proprietor / Partner / Director(s)':  'Passport',
    'Copy of Passport - proprietor / Partner / Director(s) ':  'Passport',
    'Copy of Passport - proprietor / Partner / Director(s) _1':  'Passport',
    'Copy of Passport - proprietor / Partner / Director(s) _2':  'Passport',
    'Proof of Income Tax PAN ': 'Pan card',
    'Proof of Income Tax PAN': 'Pan card',
    'Service Tax Certificate': 'Service tax',
    'Service Tax Certificate ': 'Service tax',
    'Bank statement of the previews 3 months': 'Bank statement',
    'Bank statement of the previous 3 months': 'Bank statement',
    'CST & LST Registration proof': 'CST & LST',
    'Memorandum & Articles of Association / Partnership Agreements': 'Memorandum & Articles',
    'Latest Audit Accounts with Income Tax return acknowledgment copy': 'Audits'
}


class Command(BaseCommand):
    help = 'This command will migrate inactive new partner documents!'
    docs_dict = dict()

    def handle(self, *args, **options):
        print('Migrating in-active partner documents!')
        partner_list_csv = os.path.join(settings.BASE_DIR, 'migrations', 'partners.csv')
        docs_list_csv = os.path.join(settings.BASE_DIR, 'migrations', 'Doc_List.csv')

        with open(docs_list_csv, 'r', encoding='latin1') as csv_file:
            ''' Construct docs list csv file to JSON '''
            for row in list(csv.reader(csv_file)):
                if row[2] not in self.docs_dict:
                    self.docs_dict[row[2]] = []

                self.docs_dict[row[2]].append(
                    {
                        'type': row[0],
                        'file': row[1]
                    }
                )

        with open(partner_list_csv, 'r', encoding='latin1') as csv_file:
            ''' Reading csv file line by line'''
            for row in list(csv.reader(csv_file)):
                if self.is_inactive_partner(row[24]):
                    try:
                        print('Creating partner: %s' % row[0])
                        self.create_partner(row)
                    except Exception:
                        print('Failed: %s' % row[0])
                        continue

    def is_inactive_partner(self, credit):
        if not credit:
            return True
        return False

    def create_partner(self, row):
        """
        Function to store in-active partner details in database
        :param row:
        :return:
        """
        partner = InitialPartner()
        partner.credits = None
        partner.key = get_random_string(length=16)
        partner.status = 0 if not row[23] else 1
        partner.registration_status = 3
        partner.jba_code = row[23]
        partner.existing_status = 0 if not row[23] else 1
        partner.company_name = row[3]
        partner.address_1 = row[4]
        partner.address_2 = row[5]
        partner.address_3 = row[6]
        partner.city = row[7]
        partner.state = row[8]
        partner.pin_code = row[9]
        partner.preferred_user_name = row[0]
        partner.partner_type = self.construct_partner_type_str(row[25])
        partner.business_type = '1'
        partner.focused_customer = None
        partner.interested_workload = None
        partner.vendor_list = None
        partner.save()

        ''' Storing contact details '''
        self.store_contacts(partner.id, row)

        ''' Storing documents details '''
        self.store_documents(partner)

    def store_contacts(self, partner, row):
        """
        partner -> partner id, row -> row of details of csv
        :param partner:
        :param row:
        :return:
        """
        for type in CONTACT_TYPE:
            contact = InitialContactDetails()
            contact.type = type
            contact.partner_id = partner
            contact.name = row[10] +' '+ row[11]
            contact.mobile = row[12]
            contact.email = row[13]
            contact.save()

    def store_documents(self, partner):
        """
        partner -> partner object
        :param partner:
        :return:
        """
        if partner.preferred_user_name and partner.preferred_user_name in self.docs_dict:
            for docs in self.docs_dict[partner.preferred_user_name]:
                if docs and docs['type'] in DOCS_TYPES:
                    document = InitialDocumentDetails()
                    document.partner_id = partner.id
                    document.type = DOCS_TYPES[docs['type']]
                    document.file_name = docs['file']
                    document.file_data = os.path.join('documents/partner_doc', docs['file'])
                    document.save()

    def construct_partner_type_str(self, partner_type_str):
        partner_type = ''
        for i, type in enumerate(partner_type_str.split(',')):
            if type and type in PARTNER_TYPE:
                partner_type = str(i) if i == 0 else partner_type + ',' + str(i)

        return partner_type

