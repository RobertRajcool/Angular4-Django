#!/usr/bin/env python

import requests
import os
import json

from pprint import pprint

csp_domain = 'RILSBox.onmicrosoft.com'
client_id = '2e082679-29b6-4308-a408-71a6da4dc9aa'
client_secret = 'sUHhM79DbRpprgzXyWKl3I5s0MC6TqMIS/5Yw0Mp5S8='

short_hash_data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'resource': 'https://graph.windows.net'
}
short_hash_out= requests.post('https://login.windows.net/{}/oauth2/token'.format(csp_domain), data=short_hash_data)

if short_hash_out.status_code == 200:
    short_hash_token = short_hash_out.json()['access_token']

    # GEt the longer JWT token
    jwt_header = {
        'Authorization': 'Bearer %s' %(short_hash_token,)
    }
    jwt_data = { 'grant_type': 'jwt_token'}

    jwt_token_out = requests.post('https://api.partnercenter.microsoft.com/generatetoken', headers=jwt_header,
                                  data=jwt_data)
    if jwt_token_out.status_code == 200:
        jwt_token = jwt_token_out.json()['access_token']

        # Make the calls now
        access_headers = {'Authorization': 'Bearer %s' % (jwt_token,), 'Accept': 'application/json'}
        offers_out = requests.get('https://api.partnercenter.microsoft.com/v1/offers?country=IN', headers=access_headers)
        offers_out.encoding = 'utf-8-sig'
        offers_hash = json.loads(offers_out.text)

        offers = len(offers_hash['items'])
        pprint("Total number of Items: %d" %(offers,))
    else:
        pprint("Error Getting Long token")
        os.exit(-1)
else:
    pprint("Error Getting Short Token")
    os.exit(-1)