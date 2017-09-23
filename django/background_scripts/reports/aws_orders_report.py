import datetime
import calendar
from dateutil.tz import tzlocal
from cloudapp.defaults import AppDefaults
from common.reports.ReportList import ReportList
from common.mails.BaseMails import BaseMails
from django.db.models import F, Value, FloatField
from orders.models import Orders, OrderItems, order_statuses
from customers.models import CloudAccounts
from common.signals import send_mail_notifications
import os


class AwsOrdersReportGenerator:
    def __init__(self, **kwargs):
        self.t_zone = tzlocal()

        self.range = kwargs.get('range', 'month')
        date = datetime.datetime.strptime(kwargs['date'], '%d-%m-%Y') if 'date' in kwargs \
            else datetime.date.today()

        if self.range == 'month':
            """ Selecting start , end dates of month """
            day_range = calendar.monthrange(date.year, date.month)

            self.start_date = datetime.datetime(year=date.year,
                                                month=date.month,
                                                day=1,
                                                tzinfo=self.t_zone)

            self.end_date = datetime.datetime(year=date.year,
                                              month=date.month,
                                              day=day_range[1],
                                              tzinfo=self.t_zone)

        elif self.range == 'week':
            """ Selecting start , end dates of week """
            year, week_of_year, day_of_week = date.isocalendar()
            wfd = None
            if day_of_week == 7:
                wfd = date
            else:
                wfd = date - datetime.timedelta(days=day_of_week)
            wld = wfd + datetime.timedelta(days=6)

            self.start_date = datetime.datetime(year=wfd.year,
                                                month=wfd.month,
                                                day=wfd.day,
                                                tzinfo=self.t_zone)

            self.end_date = datetime.datetime(year=wld.year,
                                              month=wld.month,
                                              day=wld.day,
                                              tzinfo=self.t_zone)

        self.end_date += datetime.timedelta(days=1) - datetime.timedelta(milliseconds=1)

    def generate_report(self):
        order_items = OrderItems.objects.filter(
            order__vendor__vendor_name=AppDefaults.cloud_vendor_codes(return_as='name', query_str='AWS'),
            order__created_at__gte=self.start_date,
            order__created_at__lte=self.end_date
        )

        orders_data_list = order_items \
            .annotate(order_number=F('order__order_number'),
                      order_status=F('order__status'),
                      partner=F('order__partner__company_name'),
                      partner_jbacode=F('order__partner__jba_code'),
                      customer=F('order__customer__company_name'),
                      customer_id=F('order__customer__id'),
                      total_cost=F('order__total_cost'),
                      machine_image_name=F('cloudtemplate__image__name'),
                      machine_storage_name=F('cloudtemplate__storage__name')
                      ) \
            .values('order_number',
                    'order_status',
                    'partner',
                    'partner_jbacode',
                    'customer',
                    'customer_id',
                    'machine_image_name',
                    'machine_storage_name',
                    'quantity',
                    'discount',
                    'cost',
                    'total_cost')

        for order in orders_data_list:
            order['order_status'] = list(filter(lambda s: s[0] == order['order_status'], order_statuses))[0][1]
            order['product_name'] = order.pop('machine_storage_name') \
                if order['machine_storage_name'] is not None \
                else order.pop('machine_image_name')

            """ Fetching customer's cloud account details """
            cloud_acc_details = {'iam_username': '', 'payer_account_id': '', 'iam_url': '',
                                 'friendly_name': '', 'account_id': '',
                                 'delivery_sequence': '', 'mrr': '', 'workload': '',
                                 'reference_number': '', 'estimate_url': '', 'root_email': ''}
            ca = CloudAccounts.objects.filter(type='AWS', customer__pk=order['customer_id'])
            if ca.exists():
                ca = ca.first()
                cloud_acc_details.update({
                    'payer_account_id': ca.details.get('payer_account_id', ''),
                    'account_id': ca.details.get('account_id', ''),
                    'iam_url': ca.details.get('iam_url', ''),
                    'root_email': ca.details.get('root_email', ''),
                    'reference_number': ca.details.get('reference_number', ''),
                    'delivery_sequence': ca.details.get('delivery_sequence', ''),
                    'mrr': ca.details.get('mrr', ''),
                    'workload': ca.details.get('workload', ''),
                    'estimate_url': ca.details.get('estimate_url', '')
                })
            order.update(cloud_acc_details)

        file_generator = ReportList()

        file_response = file_generator.export(report_name='aws_orders_report',
                                              screen_name='aws_orders_report_{}_to_{}'.format(
                                                  self.start_date.strftime('%Y_%m_%d'),
                                                  self.end_date.strftime('%Y_%m_%d')
                                              ),
                                              export_type='csv',
                                              data_list=orders_data_list)

        headers = file_response._headers
        attachments = [
            {
                'filename': headers['content-disposition'][1].split(';')[1].split('=')[1],
                'content': file_response.content,
                'mimetype': headers['content-type'][1]
            }
        ]

        """ Sending Emails """
        send_mail_notifications.send(sender=Orders,
                                     trigger='AwsOrdersReport',
                                     details={
                                         'subject': 'AWS ORDERS {}LY REPORT'.format(self.range.upper()),
                                         'message': 'Please find the AWS orders report file for the duration : %s to %s' % (
                                             self.start_date.date(), self.end_date.date()),
                                         'attachments': attachments
                                     })

        return True
