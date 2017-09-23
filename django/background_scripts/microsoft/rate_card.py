from . import microsoft_base
from redington import settings
from cloudtemplates.models import CloudRates
from products.models import Products
from django.db.models import ObjectDoesNotExist
from cloudapp.defaults import AppDefaults

import requests
import subprocess
import os.path
import json


class RateCard(microsoft_base.MicrosoftBase):
    def __init__(self):
        super(RateCard, self).__init__()
        self.ratecard_file = '/tmp/ratecard.json'

    def storeRateCard(self):
        access_headers = self.getAccessHeaders()

        rate_card_url = 'https://api.partnercenter.microsoft.com/v1/ratecards/azure?currency=INR&region=IN'
        ratecard_out = requests.get(rate_card_url, headers=access_headers)
        ratecard_out.encoding = 'utf-8-sig'
        ratecard = ratecard_out.text
        out_file = open(self.ratecard_file, 'w')
        out_file.write(ratecard)
        out_file.close()

        if os.path.exists(self.ratecard_file):
            proc = subprocess.Popen(
                ["jq", "-c", '.meters[] | [.id, .category,.subcategory, .region, .name, .rates."0"]'],
                stdout=subprocess.PIPE, stdin=open(self.ratecard_file))

            azure_product = Products.objects.filter(
                            vendor_details__vendor_name=AppDefaults.cloud_vendor_codes(
                                return_as='name',
                                query_str='MS')).first()

            for line in proc.stdout.readlines():
                line = json.loads(line.decode('utf-8'))

                try:
                    obj = CloudRates.objects.get(uuid=line[0])
                    obj.rate = line[5]
                    obj.save()
                    print("Updated for %s in region %s" % (line[3], line[2]))
                except ObjectDoesNotExist:
                    CloudRates.objects.create(
                        product=azure_product,
                        rateName=line[4],
                        region=line[3],
                        category=line[1],
                        subcategory=line[2],
                        rate=line[5],
                        uuid=line[0]
                    )
                    print("Inserted for %s in region %s" % (line[3], line[2]))
