import requests

class MicrosoftBase(object):
    def __init__(self):
        self.csp_domain = 'RILSBox.onmicrosoft.com'
        self.client_id = '2e082679-29b6-4308-a408-71a6da4dc9aa'
        self.client_secret = 'sUHhM79DbRpprgzXyWKl3I5s0MC6TqMIS/5Yw0Mp5S8='
        #self.csp_domain = 'rilcsp.onmicrosoft.com'
        #self.client_id = '931aa137-f8d8-47ec-b6f5-8cfe749ea28a'
        #self.client_secret = 'O4WBcX+EEU8V50bwlyPRVxnPJGschIKnAjhGR5DchfI='


    def getAccessHeaders(self):

        short_hash_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': 'https://graph.windows.net'
        }
        short_hash_out = requests.post('https://login.windows.net/{}/oauth2/token'.format(self.csp_domain),
                                       data=short_hash_data)

        access_headers = None
        if short_hash_out.status_code == 200:
            short_hash_token = short_hash_out.json()['access_token']

            # Make the calls now
            access_headers = {'Authorization': 'Bearer %s' % (short_hash_token,), 'Accept': 'application/json'}

        access_headers = {'Authorization': 'Bearer %s' % (short_hash_token,), 'Accept': 'application/json'}
        return access_headers