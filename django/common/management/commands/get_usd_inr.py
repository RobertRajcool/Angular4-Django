from django.core.management import BaseCommand
import requests
import datetime
from common.models import ConversionRates

from redington.settings import OPENEXCHANGE_KEY

class Command(BaseCommand):
    help = "This command will fetch the USD-INR and store in database"

    def handle(self, *args, **kwargs):
        try:
            currencies_out = requests.get(str.format('https://openexchangerates.org/api/latest.json?app_id={}', OPENEXCHANGE_KEY))
            if currencies_out.status_code == 200:
                currencies = currencies_out.json()
                inr_rate = currencies['rates']['INR']
                if ConversionRates.objects.filter(id=1).count() == 0:
                    conversionRate = ConversionRates()
                    conversionRate.rate = inr_rate
                    conversionRate.created_at = datetime.datetime.now()
                    conversionRate.save()
                else:
                    conversion_Rate_object = ConversionRates.objects.get(id=1)
                    conversion_Rate_object.rate = inr_rate
                    conversion_Rate_object.created_at = datetime.datetime.now()
                    conversion_Rate_object.save()

                print("Got INR Conversion Rate of ", inr_rate, "at ", datetime.datetime.now())
        except Exception as e:
            from cloudapp.generics.functions import get_traceback
            exception = get_traceback(e)
            from common.mails.BaseMails import BaseMails
            from cloudapp.generics.constant import AppContants
            BaseMails.send_mail(subject='REDINGTON: Throws error get inr value  value',
                                recipients=['doss.cclawrance226@gmail.com'],
                                template_name='product_error.html',
                                template_data={'details': exception})