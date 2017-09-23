import csv
import datetime
import os
import json

from django.conf import settings
from django.core.management import BaseCommand

from cloudapp.defaults import AppDefaults
from partner.models import Partner, ContactDetails, PartnerUserDetails
from users.models import RedUser, UserProfile, Group
from customers.models import Customers, CustomerContacts

# RAJA: TODO: Remember to change users_reduser firstname/lastname to varchar(100) as some names are long
class Command(BaseCommand):
    help = "This command migrates from old Redington cloud Delta to new system"

    def handle(self, *args, **options):
        migration_csvs = os.path.join(settings.BASE_DIR, 'migrations')

        partner_map = {}

        print("Creating Partners...")
        with open(os.path.join(migration_csvs, 'partners_delta.csv'), 'r', encoding='latin1') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row[0]:
                    print("Cannot find partner identifier for ", row[0])
                    continue

                partner = Partner.objects.filter(jba_code = str.strip(row[23]))
                if partner:
                    partner_map[row[0].strip()] = partner[0].id
                    continue

                print("New Partner: %s" %(row[0]))

                partner = Partner()
                partner.company_name = row[3]

                if row[1] == 'Y':
                    partner.status = True
                else:
                    partner.status = False

                if row[28] == 'Y':
                    partner.existing_status = True
                else:
                    partner.existing_status = False
                partner.jba_code = str.strip(row[23])
                partner.credits = row[24]
                partner.address_1 = row[4]
                partner.address_2 = row[5]
                partner.address_3 = row[6]
                partner.city = row[7]
                partner.state = row[8]
                partner.pin_code = row[9]
                partner.partner_type = 'R'
                partner.business_type = 'S'
                partner.focused_customer = ''
                partner.business_type = ''
                partner.interested_workload = ''
                original_date = row[21].split(' ')
                try:
                    val = datetime.datetime.strptime(original_date[0], '%m/%d/%y')
                except ValueError:
                    val = datetime.datetime.strptime(original_date[0], '%m/%d/%Y')
                partner.created_at = val
                partner.activated_at = val
                for field in partner._meta.fields:
                    if field.name == 'created_at' or field.name == 'activated_at':
                        field.auto_now_add = False
                partner.created_by = 1
                partner.save()
                partner_id = partner.id
                partner_map[row[0].strip()] = partner_id

                c = ContactDetails()
                c.partner = partner
                c.type = 'P'
                c.name = str.format('{} {}', row[10], row[11])
                c.email = row[13]
                c.mobile = row[12]
                c.save()

                contact_types = ['D/O', 'A&O', 'S']
                for type in contact_types:
                    c = ContactDetails()
                    c.partner = partner
                    c.type = type
                    c.name = str.format('{} {}', row[10], row[11])
                    c.email = row[13]
                    c.mobile = row[12]
                    c.save()


        print("Creating Customers...")
        import pdb;pdb.set_trace()
        import json
        customer_map = json.load(open('/tmp/customer_map.json','r'))
        with open(os.path.join(migration_csvs, 'customers_delta.csv'), 'r', encoding='latin1') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                customer = Customers()
                if not row[1].strip() in partner_map.keys():
                    print("Cannot find partner for customer: ", row[1])
                    continue

                if row[0] in customer_map:
                    continue

                print("New customer: %s" %(row[0]))
                customer.partner_id = partner_map[row[1].strip()]
                customer.company_name = row[2]
                customer.address = row[3]
                customer.city = row[6]
                customer.state = row[7]
                customer.country = row[8]
                customer.Pincode = row[9]
                customer.pan_number = row[22]
                customer.deleted = False
                original_date = row[24].split(' ')
                try:
                    val = datetime.datetime.strptime(original_date[0], '%m/%d/%y')
                except ValueError:
                    val = datetime.datetime.strptime(original_date[0], '%m/%d/%Y')
                customer.created_at = val
                for field in customer._meta.fields:
                    if field.name == 'created_at':
                        field.auto_now_add = False

                customer.save()
                customer_map[row[0]] = customer.id

                customer_contact = CustomerContacts()
                customer_contact.customer = customer
                customer_contact.name = str.format('{} {} {}', row[10], row[11], row[12])
                customer_contact.position = row[13]
                customer_contact.email = row[15]
                customer_contact.mobile = row[14]
                customer_contact.save()

                customer_contact2 = CustomerContacts()
                customer_contact2.customer = customer
                customer_contact2.name = str.format('{} {} {}', row[16], row[17], row[18])
                customer_contact2.position = row[19]
                customer_contact2.email = row[21]
                customer_contact2.mobile = row[20]
                customer_contact2.save()

        import json
        customer_contents = json.dumps(customer_map)
        f = open('/tmp/customer_map.json', 'w')
        f.write(customer_contents)
        f.close()

        print("Creating Users...")
        with open(os.path.join(migration_csvs, 'users_delta.csv'), 'r', encoding='latin1') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not row[3].strip() in partner_map.keys():
                    print("Cannot find partner for user: ", row[3])
                    continue

                if row[2] == 'TRUE':
                    print("Found Redington user: {}, Please create manually", row[3])
                    continue

                user = RedUser.objects.filter(username = str.strip(row[3]))
                if user:
                    continue

                print("New User: %s" %(row[3]))

                user = RedUser()
                user.username = row[3]
                user.first_name = row[4]
                user.last_name = row[5]
                user.email = row[6]
                user.is_active = True
                user.is_staff = False
                user.save()

                permission_group_name = AppDefaults.get_predefined_roles()

                if Group.objects.filter(name=permission_group_name['Partner']).exists():
                    user.groups = Group.objects.filter(name=permission_group_name['Partner'])
                    user.save()

                PartnerUserDetails.objects.create(user=user,
                                                  partner= Partner.objects.get(pk=partner_map[row[3].strip()]))

                UserProfile.objects.create(
                    user = user,
                    user_type = 'P',
                    description = str.format('Partner user for {}', row[3]),
                    created_by = RedUser.objects.get(username='Administrator'),
                    role_id = 2
                )
