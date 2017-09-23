import os
import csv
from redington import settings
from django.core.management import BaseCommand
from partner.models import Partner, PartnerUserDetails, DocumentDetails
from users.models import RedUser

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
    help = 'This command will migrate active partner documents!'
    docs_jba_dict = dict()
    docs_username_dic = dict()

    def handle(self, *args, **options):
        print('Migrating active partner documents!')
        docs_list_csv = os.path.join(settings.BASE_DIR, 'migrations', 'Doc_List.csv')

        with open(docs_list_csv, 'r', encoding='latin1') as csv_file:
            ''' Construct docs list csv file to JSON '''
            for row in list(csv.reader(csv_file)):
                if row[3] not in self.docs_jba_dict:
                    self.docs_jba_dict[row[3]] = []

                self.docs_jba_dict[row[3]].append(
                    {
                        'type': row[0],
                        'file': row[1]
                    }
                )

                if row[2] not in self.docs_username_dic:
                    self.docs_username_dic[row[2]] = []

                    self.docs_username_dic[row[2]].append(
                        {
                            'type': row[0],
                            'file': row[1]
                        }
                    )

        for partner in list(Partner.objects.all()):
            if partner.jba_code and partner.jba_code in self.docs_jba_dict:
                ''' Storing documents if JBA code matches '''
                try:
                    print('%s: Storing documents in progress..' % partner.company_name)
                    self.store_documents(partner.id, self.docs_jba_dict[partner.jba_code])
                    print('%s: Completed !' % partner.company_name)
                except Exception:
                    print('Failed: Exception occurred !')
                    continue

            elif self.get_username(partner.id):
                ''' Storing documents if username matches '''
                user = self.get_username(partner.id)
                if user in self.docs_username_dic:
                    try:
                        print('%s: Storing documents in progress..' % partner.company_name)
                        self.store_documents(partner.id, self.docs_username_dic[user])
                        print('%s: Completed !' % partner.company_name)
                    except Exception:
                        print('Failed: Exception occurred !')
                        continue
                else:
                    print('%s: not exists !' % partner.company_name)
            else:
                print('%s: not exists !' % partner.company_name)

    def get_username(self, partner):
        """
        partner -> partner id
        :param partner:
        :return:
        """
        user = PartnerUserDetails.objects.filter(partner_id=partner).first()
        if user:
            return RedUser.objects.get(pk=user.user_id).username
        else:
            return False

    def store_documents(self, partner, documents):
        """
        partner -> partner id, documents -> list of documents in csv file
        :param partner:
        :param documents:
        :return:
        """
        for docs in documents:
            if docs and docs['type'] in DOCS_TYPES:
                document = DocumentDetails()
                document.partner_id = partner
                document.type = DOCS_TYPES[docs['type']]
                document.file_name = docs['file']
                document.file_data = os.path.join('documents/partner_doc', docs['file'])
                document.save()