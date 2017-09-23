from django.core.management import BaseCommand


class Command(BaseCommand):

    help = "To get partner contact details"

    def handle(self, *args,**options):
        # read the all from csv file
        from django.db import connection
        cursor = connection.cursor()
        query = ' select b.company_name, a.name, a.email, a.mobile, b.jba_code from partner_contactdetails a ' \
                'left join partner_partner b on a.partner_id = b.id '
        cursor.execute(query)
        records = cursor.fetchall()
        if len(records) != 0:
            file_name = 'monthly_invoices.csv'
            import csv
            header = ('Company Name', 'Name', 'Email', 'Mobile', 'JBA Code')

            with open('/tmp/' + file_name, "w") as csv_file:
                wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                wr.writerow(header)
                for list_record in records:
                    wr.writerow(list_record)
                csv_file.close()
            csv_file_url = '/tmp/' + file_name
            print(csv_file_url)