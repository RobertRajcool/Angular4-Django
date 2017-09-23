import datetime
from partner.models import Partner
from customers.models import CloudAccounts
from orders.models import Subscriptions
from background_scripts.microsoft.get_utilization import UtilizationRecords
from django.conf import settings
from common.mails.BaseMails import BaseMails
import os


class GetAzureUtilizationByPartner:
    log_dir = "/var/log/scripts"
    log_file = "azure_utilization.log"

    def __init__(self, partner, start_date, end_date):
        self.partner = partner
        self.start_date = start_date.isoformat() + 'Z'
        self.end_date = end_date.isoformat() + 'Z'

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    # Main method to get the vm list
    def getUtilization(self):

        azure_subscriptions = Subscriptions.objects.filter(
            customer__in=Partner.objects.get(pk=self.partner).customers_set.all(),
            name='Microsoft Azure',
            status='active')

        log_file = open(os.path.join(self.log_dir, self.log_file), 'a')
        log_file.write('<%s>\n' % ('-' * 120,))
        log_file.write('%s %s <-> %s\n' % ((' ' * 35), self.start_date, self.end_date))
        log_file.write('<%s>\n' % ('-' * 120,))
        fails = list()
        for subscription in azure_subscriptions:
            try:
                cloudaccount = CloudAccounts.objects.filter(type='MS', customer=subscription.customer)

                if cloudaccount.exists():
                    cloudaccount = cloudaccount.first()
                else:
                    raise ValueError('Seems there is no cloud account for %s' % cloudaccount.customer.company_name)

                # Azure tenant id
                tenant_id = cloudaccount.details.get('tenant_id', None)

                if not tenant_id:
                    raise ValueError('Seems there is no tenant ID for %s' % cloudaccount.customer.company_name)

                print(tenant_id, subscription.subscription, self.start_date, self.end_date)
                util = UtilizationRecords(tenantId=tenant_id,
                                          subscriptionId=subscription.subscription,
                                          startDate=self.start_date,
                                          endDate=self.end_date)
                util.getUtilization()

                success = 'Loaded utilization for subscription : %s \n\n' % (subscription.subscription,)
                print(success)
                # log_file.write(success)

            except Exception as e:
                error_title = 'Failed to fetch utilization for subscription : %s \n ' % subscription.subscription
                print(error_title)
                print(str(e))
                log_file.write(error_title)
                log_file.write('%s \n' % str(e))

                fails.append({
                    'subscription': subscription.subscription,
                    'error': str(e)
                })
                continue

        if len(fails) > 0:
            """ Error notification """

            content = "<p><strong>Failed to fetch utilization on the following cases : </strong></p>"
            content += "<table><thead><tr><th style='min-width: 300px;'>Subscription</th><th>Error</th></tr></thead><tbody>"

            for fail in fails:
                content += "<tr><td>%s</td><td>%s</td></tr>" % (fail['subscription'], fail['error'])

            content += "</tbody></table>"

            BaseMails.send_mail(subject='ERROR: Loading Azure bills into database',
                                recipients=settings.TECH_TEAM,
                                template_name='plain.html',
                                template_data={
                                    'Title': 'ERROR',
                                    'message': content
                                }
                                )

        log_file.close()
