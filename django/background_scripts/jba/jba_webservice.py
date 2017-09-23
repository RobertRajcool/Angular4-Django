import requests
from background_scripts.jba.jba_apis import PARTNER_DETAILS_API, ORDER_POSTING_API, DELIVERY_SEQUENCE_API
import datetime
from rest_framework import status
import json
from common.models import ConversionRates
from django.conf import settings
import os
from django.utils import timezone
from cloudapp.generics.functions import generate_web_so_number
from customers.models import Customers
from time import gmtime, strftime
from cloudapp.defaults import AppDefaults


class JBAWebService:
    def __init__(self):
        self.exchange_rate = ConversionRates.objects.first().rate

    def fetch_partner_details(self, partner_details):
        """
        Function to fetch partner details from JBA

        :param partner_details: Partner details dict
        :returns success: partners_jba_details, status_code
        :returns fail: error_msg, status_code
        """

        """ JBA Call to get partner details """
        partner_details_response = requests.get(PARTNER_DETAILS_API,
                                                params={'Customercode': partner_details['jba_code']})

        # Handling webservice call errors
        if partner_details_response.status_code != 200:
            return "Failed to fetch partner details from JBA : %s" % partner_details_response.json(), \
                   partner_details_response.status_code
        elif len(partner_details_response.json()) == 0:
            return "No details found for partner in JBA", status.HTTP_404_NOT_FOUND

        return partner_details_response.json()[0], 200

    '''
        def post_to_invoice_api(self, bill_details, post_from='PORTAL'):
        """
        Functions to post order into JBA for invoice generation

        :param bill_details: Order details dict
        :returns success: posted data, status_code
        :returns fail: error_msg, status_code
        """

        if post_from == 'PORTAL':
            order_states = {l[1]: l[0] for l in order_statuses}
            if order_states[bill_details['status']] >= 5 and 'amendment' not in bill_details:
                return "It seems order already posted to JBA", status.HTTP_200_OK, None

            bill_details['client_details'] = bill_details.pop('partner_details')
            bill_details['client_jba_code'] = bill_details.pop('partner_jba_code')

        elif post_from == 'ISV_PORTAL':
            service_states = {l[1]: l[0] for l in ISV_SERVICE_STATUSES}
            if service_states[bill_details['status']] >= 4:
                return "It seems order already posted to JBA", status.HTTP_200_OK, None

            bill_details['client_jba_code'] = bill_details.pop('isv_jba_code')
            bill_details['client_details'] = {'jba_code': bill_details['client_jba_code']}

        client = bill_details['client_details']

        client_details, status_code = self.fetch_partner_details(partner_details=client)
        if status_code != 200:
            return client_details, status_code, None

        due_date = datetime.date.today() + datetime.timedelta(days=int(client_details['CreditDay']))

        """ Generate Web SO """
        web_so = self.generate_webso(bill_details=bill_details, post_from=post_from)

        """ Generate unique PI """
        pi_number_with_unique_string = ''

        if isinstance(web_so.order, CloudSalesOrders):
            bill_details['order_number'] = web_so.web_order_number

            if web_so.order.vendor.vendor_name == AppDefaults.cloud_vendor_codes(return_as='name', query_str='AWS'):
                pi_number_with_unique_string = str.format('{}/{}'
                                                          , bill_details['pi_number'][0:9]
                                                          , web_so.web_order_number)
            elif web_so.order.vendor.vendor_name == AppDefaults.cloud_vendor_codes(return_as='name', query_str='MS'):
                pi_number_with_unique_string = str.format('{}/{}'
                                                          , bill_details['pi_number'][0:9]
                                                          , web_so.web_order_number)
        else:
            current_date_time = strftime("%y%m%d%H%M", gmtime())
            pi_number_with_unique_string = str.format('{}/{}'
                                                      , bill_details['pi_number'][0:9]
                                                      , current_date_time)

        if 'Del_Seq' not in bill_details:
            bill_details['Del_Seq'] = web_so.order.customer.delivery_sequence

        order = {
            "Order_Number": web_so.web_order_number,
            "CustomerCode": bill_details['client_jba_code'],
            "DueDate": str.format('1{}', datetime.date.strftime(due_date, "%y%m%d")),
            "EcAccId": '',
            "PONumber": pi_number_with_unique_string[0:20],
            "Del_Seq": bill_details['Del_Seq'] if 'Del_Seq' in bill_details and bill_details['Del_Seq'] and
                                                  bill_details['Del_Seq'] != '' else '000',
            "Items": []
        }

        # EcAccId
        if 'EcAccId' in bill_details:
            order['EcAccId'] = bill_details['EcAccId'][0:25] if len(bill_details['EcAccId']) > 25 else bill_details['EcAccId']

        # Delivery sequence
        if 'Del_Seq' in bill_details:
            order['Del_Seq'] = bill_details['Del_Seq']

        for item in bill_details['items']:
            item['cost'] = float(item['cost']) / item['quantity']
            if bill_details['currency'] == 'USD':
                item['cost'] *= float(self.exchange_rate)

            item_details = {
                "itemCode": item['jba_code'],
                "lineQty": item['quantity'],
                "unitPrice": item['cost'],
                "cashDiscount": '0',
                "Location": "C1",
            }

            if 'stock_location' in item and item['stock_location'] != '':
                item_details['Location'] = item['stock_location']

            order['Items'].append(item_details)

        """ JBA Webservice call to posting order """
        headers = {'Content-Type': 'application/json'}
        order_post_response = requests.post(ORDER_POSTING_API, data=json.dumps(order), headers=headers)
        self.write_to_file(sales_order=order, status_code=order_post_response.status_code)

        # Changing order status
        if order_post_response.status_code == 200 and order_post_response.json() == "Y":
            web_so.posted = True
            web_so.save()

            order_instance = web_so.order
            if isinstance(order_instance, CloudSalesOrders):
                order_instance.status = 1
                order_instance.save()

            return bill_details, 200, order

        # Handling webservice call errors
        else:
            return "Failed to post order into JBA :%s" % order_post_response.json(), \
                   status.HTTP_500_INTERNAL_SERVER_ERROR, order

    '''

    def fetch_partner_delivery_sequence(self, partner_jba_code):
        """
        Function to fetch partner's delivery sequences from JBA

        :param partner_jba_code: Partner' jba code
        :returns success: partners_delivery_sequences, status_code
        :returns fail: error_msg, status_code
        """

        """ JBA Call to get partner's delivery sequences """
        delivery_sequence_response = requests.get(DELIVERY_SEQUENCE_API, params={'Customercode': partner_jba_code})

        # Handling webservice call errors
        if delivery_sequence_response.status_code != 200:
            return "Failed to fetch delivery sequence from JBA : %s" % delivery_sequence_response.json(), \
                   delivery_sequence_response.status_code
        elif len(delivery_sequence_response.json()) == 0:
            return "No delivery sequence found for partner in JBA", status.HTTP_404_NOT_FOUND

        return delivery_sequence_response.json(), 200
    '''
        def write_to_file(self, sales_order, status_code):
        """ Writing sales order data into json file """

        sales_order = {
            'posted_at': datetime.datetime.strftime(timezone.localtime(timezone.now()), "%Y-%m-%d %H:%M:%S"),
            'response_code': status_code,
            'data': sales_order
        }

        path = os.path.join(settings.BASE_DIR, 'invoices', 'sales_orders', 'posted_to_jba.json')

        mode = 'r+' if os.path.exists(path) else 'w+'

        with open(path, mode) as json_file:
            content = json_file.read()

            if content is not None and content != '':
                data = json.loads(content)
                data.append(sales_order)
            else:
                data = [sales_order]

            json_file.seek(0)
            json_file.truncate()

            json.dump(data, json_file, indent=2, sort_keys=True)
            json_file.close()

        print('Sales order written into : ', path)

    def generate_webso(self, bill_details, post_from):
        order_instance = None
        order_discount = 0
        order_cost = 0

        if post_from == 'PORTAL' and bill_details['order_number'] and bill_details['order_number'] != '':
            order_instance = Orders.objects.get(order_number=bill_details['order_number'])
        elif post_from == 'PORTAL':
            """ Creating cloud sales order instance """
            order_instance = CloudSalesOrders.objects.create(customer_id=bill_details['customer_details']['id'],
                                                             vendor_id=bill_details['vendor_id'],
                                                             product_id=bill_details['product_id'],
                                                             invoice_id=bill_details[
                                                                 'invoice_id'] if 'invoice_id' in bill_details.keys() else None,
                                                             billing_date=bill_details['billing_date'],
                                                             status=0)
            order_instance.save()

            for item in bill_details['items']:
                order_discount += round(float(item.get('discount', '0')), 2)
                order_cost += round(float(item.get('cost', 0)), 2)

        elif post_from == 'ISV_PORTAL':
            order_instance = IsvMarketplaceService.objects.get(id=bill_details['record_id'])

        """ Creating Web SO instance """
        web_so_instance = WebSalesOrders.objects.create(web_order_number=generate_web_so_number(),
                                                        order=order_instance,
                                                        details={
                                                            'cost': order_cost,
                                                            'discount': order_discount
                                                        } if isinstance(order_instance, CloudSalesOrders) else None,
                                                        posted=False
                                                        )
        web_so_instance.save()

        return web_so_instance
    '''

