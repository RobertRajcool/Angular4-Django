import os
import csv
import datetime
from redington import settings
from django.core.management import BaseCommand
from customers.models import Customers, CustomerContacts
from partner.models import Partner, ContactDetails
from invoices.models import InvoiceDetails


class Command(BaseCommand):
    help = 'This command migrates invoice details'
    partner = ''
    customer = ''

    def handle(self, *args, **options):
        print('Migrating invoice details!')

        invoice_list_csv = os.path.join(settings.BASE_DIR, 'migrations', 'test.csv')

        with open(invoice_list_csv, 'r', encoding='latin1') as csv_file:
            ''' Reading csv file line by line  '''
            for row in list(csv.reader(csv_file)):
                print('Trying: %s' % row[1])
                if self.is_invoice_exists(row[2]):
                    self.copy_invoice_file(row)
                else:
                    if self.is_partner_exists(row[0]):
                        try:
                            self.add_invoices(row)
                            print('Succeeded: Invoice added for %s' % row[1])
                            self.copy_invoice_file(row)
                        except Exception:
                            print('Failed: Exception occurred!')
                            continue
                    else:
                        print('Failed: %s not exists' % row[1])

    def is_invoice_exists(self, invoice):
        """
        Function to check whether invoice already updated in database or not
        invoice -> invoice number
        :param invoice:
        :return:
        """
        return InvoiceDetails.objects.filter(invoice_no__icontains=invoice).exists()

    def is_file_exists(self, file):
        """
        Function to check whether pdf exists in the old invoices directory or not
        file -> pdf file path
        :param file:
        :return:
        """
        return os.path.exists(file)

    def copy_invoice_file(self, row):
        """
        Function to copy file to invoice folder
        :param row:
        :return:
        """
        src = os.path.join('/home/jba/old_invoices', row[6] + '.PDF')
        if self.is_file_exists(src):
            from shutil import copyfile
            dst = os.path.join(settings.BASE_DIR, 'invoices', 'stored_invoices', row[0],
                               str.format('{}.pdf', row[2]))
            if self.is_dir_exists(os.path.join(settings.BASE_DIR, 'invoices', 'stored_invoices', row[0])):
                copyfile(src, dst)
            print('%s moved!' % row[6])
        else:
            print('%s not exists !' % row[2])

    def is_dir_exists(self, dir):
        """
        Function to check directory exists else make directory
        :param dir:
        :return:
        """
        if not os.path.exists(dir):
            os.makedirs(dir)
        return True

    def is_partner_exists(self, code):
        """
        Function to check whether partner available for requested JBA code
        and get customers
        code -> JBA
        :param code:
        :return:
        """
        if code and Partner.objects.filter(jba_code__icontains=code).exists():
            self.partner = Partner.objects.filter(jba_code__icontains=code).first()
            if self.partner.id and Customers.objects.filter(partner_id=self.partner.id).exists():
                self.customer = Customers.objects.filter(partner_id=self.partner.id).first()
            else:
                self.create_customer()
            return True
        else:
            return False

    def create_customer(self):
        customer = Customers()
        customer.partner_id = self.partner.id
        customer.company_name = self.partner.company_name
        customer.address = self.partner.address_1 + '' + self.partner.address_2
        customer.city = self.partner.city
        customer.state = self.partner.state
        customer.Pincode = self.partner.pin_code
        customer.country = self.partner.state
        customer.pan_number = ''
        customer.deleted = False
        customer.customer_vertical = None
        customer.delivery_sequence = '000'
        customer.save()
        print('Customer %s created' % customer.company_name)

        self.customer = customer

        ''' Creating customer contacts1 '''
        self.create_customer_contacts()

        ''' Creating customer contacts2 '''
        self.create_customer_contacts()

    def create_customer_contacts(self):
        cntct = ContactDetails.objects.filter(partner_id=self.partner.id, type='P').first()
        contacts = CustomerContacts()
        contacts.customer_id = self.customer.id
        contacts.name = cntct.name
        contacts.position = ''
        contacts.email = cntct.email
        contacts.mobile = cntct.mobile
        contacts.save()

    def add_invoices(self, row):
        invoice = InvoiceDetails()
        invoice.invoice_no = row[2]
        invoice.invoice_date = datetime.datetime.strptime(row[3], '%d/%m/%Y').replace(tzinfo=None)
        invoice.due_date = datetime.datetime.strptime(row[4], '%d/%m/%Y').replace(tzinfo=None)
        invoice.partner_id = self.partner.id
        invoice.customer_id = self.customer.id
        invoice.order = None
        invoice.invoice_total = row[5]
        invoice.grand_total = row[5]
        invoice.sales_tax = 0
        invoice.deleted = False
        invoice.created_at = datetime.datetime.now()
        invoice.payment_reference = None
        invoice.payz_app_id = ''
        invoice.save()

