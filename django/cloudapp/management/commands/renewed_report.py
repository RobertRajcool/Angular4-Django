import csv
from io import StringIO
from django.core.management import BaseCommand
from common.mails.BaseMails import BaseMails
from datetime import datetime, date


class Command(BaseCommand):

    help = "This command is to get the Renewed orders"
    recipients = ['santh2ss@gmail.com']
    csv_file_url = None
    file_name = 'renewed_orders(' + datetime.today().strftime('%d-%m-%Y') + ').csv'

    def handle(self, *args,**options):
        # read the all from csv file
        from django.db import connection
        cursor = connection.cursor()
        query = 'SELECT o.order_number, s.subscription, s.effective_start_date, s.commitment_end_date, c.company_name, p.company_name AS "Partner name", p.jba_code, o.billing_type, pr.product_name, pr.product_jbacode, s.quantity, oi.price_per_unit, s.quantity * oi.price_per_unit as "cost" FROM orders_subscriptions s LEFT JOIN orders_orders o ON s.order_id=o.id LEFT JOIN customers_customers c ON s.customer_id=c.id LEFT JOIN partner_partner p ON c.partner_id=p.id LEFT JOIN products_products pr ON s.product_id=pr.prod_id LEFT JOIN orders_orderitems oi ON s.order_id=oi.order_id and s.product_id=oi.product_id WHERE DAY(s.effective_start_date) < 23 AND YEAR(s.effective_start_date) < 2017 AND MONTH(s.effective_start_date) in (7,8) AND s.status="active" AND s.renewed=0 and s.billing_type!="usage";'

        cursor.execute(query)
        records = cursor.fetchall()

        if len(records) != 0:
            csv_file = StringIO()
            writer = csv.writer(csv_file)
            header = ['Order Number', 'Subscription ID', 'Subscription start date', 'Subscription end date',
                      'Customer name', 'Partner name', 'Partnercode',
                      'Billing Type', 'Product', 'JBA code', 'Quantity', 'Unit price', 'Total']
            writer.writerow(header)
            for list_record in records:
                list_record = list(list_record)
                writer.writerow(list_record)

            current_date = date.today()
            attachments_data = [{
                'filename': 'all_ms_order('+current_date.isoformat()+').csv',
                'content': csv_file.getvalue().encode('utf-8'),
                'mimetype': 'text/csv'
            }]

            data = dict()
            data['subject'] = 'Microsoft Order report'
            data['data'] = "Please find the attachment of microsoft renewed report."
            BaseMails.send_mail(subject='Microsoft renewed report',
                                recipients=self.recipients,
                                template_name='common_template.html',
                                template_data=data, attachements=None, attachments_full_path=None,
                                data_attachments=attachments_data)

        self.stdout.write(self.style.SUCCESS('Report sent'))
