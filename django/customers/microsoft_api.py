import requests
import json
from pprint import pprint

class MicrosoftApi:
    microsoft_login_url = 'https://login.windows.net/RILSBox.onmicrosoft.com/oauth2/token'
    ms_login_url = 'https://login.windows.net/{}/oauth2/token'
    microsoft_client_id = '577bdf93-8c60-440d-884d-ad9fadb16df1'
    base_url = 'https://api.partnercenter.microsoft.com/v1/'
    csp_domain = 'RILSBox.onmicrosoft.com'
    client_id = '2e082679-29b6-4308-a408-71a6da4dc9aa'
    client_secret = 'sUHhM79DbRpprgzXyWKl3I5s0MC6TqMIS/5Yw0Mp5S8='
    access_headers = {}

    client_id_for_azure = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'

    # This was added to validate the MPN ID
    login_data = {
        'grant_type': 'password',
        'client_id': microsoft_client_id,
        'scope': 'openid',
        'resource': 'https://api.partnercenter.microsoft.com',
        'username': 'devadmin@rilsbox.onmicrosoft.com',
        'password': 'Saibaba321'
    }

    # Normal login data
    short_hash_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'resource': 'https://graph.windows.net'
    }

    def __init__(self):
        self.microsoft_login()

    def get_domain_access_headers(self, mode, domain_name):
        """
        Function to get access headers for customer accounts
        :return:
        """
        ms_url = self.ms_login_url.format(domain_name)
        login_data = self.login_data
        login_data['client_id'] = self.client_id_for_azure
        access_headers = {}
        if mode == 'graph':
            login_data['resource'] = 'https://graph.windows.net'
        else:
            login_data['resource'] = 'https://management.azure.com/'
        short_hash_out = requests.post(ms_url, data=self.login_data)
        if short_hash_out.status_code == 200:
            short_hash_token = short_hash_out.json()['access_token']
            access_headers = {'Authorization': 'Bearer %s' % (short_hash_token,), 'Accept': 'application/json'}
        return access_headers

    def microsoft_login(self):
        """
        Microsoft login function
        :return:
        """
        short_hash_out = requests.post(self.microsoft_login_url, data=self.login_data)
        if short_hash_out.status_code == 200:
            short_hash_token = short_hash_out.json()['access_token']
            #pprint(short_hash_token)
            self.access_headers = {'Authorization': 'Bearer %s' % (short_hash_token,), 'Accept': 'application/json'}

    def ms_normal_login(self):
        short_hash_out = requests.post(self.ms_login_url.format(self.csp_domain), data=self.short_hash_data)
        if short_hash_out.status_code == 200:
            short_hash_token = short_hash_out.json()['access_token']
            self.access_headers = {'Authorization': 'Bearer %s' % (short_hash_token,), 'Accept': 'application/json'}

    def get_domain_users(self, domain_name):
        """
        Function to get all the users in given domain name
        :param domain_name:
        :return:
        """
        access_headers = self.get_domain_access_headers('graph', domain_name)
        offers_out = requests.get('https://graph.windows.net/myorganization/users?api-version=1.6',
                                  headers=access_headers)
        offers_out.encoding = 'utf-8-sig'
        offers_hash = json.loads(offers_out.text)
        result = []
        if 'value' in offers_hash:
            for data in offers_hash['value']:
                result.append(data['objectId'])
        return result

    def handle_change_ownership(self, domain_name, subscription):
        """
        Function to handle change ownership for users in given domain
        :param domain_name:
        :param subscription:
        :return:
        """
        domain_users = self.get_domain_users(domain_name)
        set_user = False
        if len(domain_users):
            set_user = self.set_owner_user(domain_name, subscription, domain_users)
        else:
            print('Unable to fetch users')
        return set_user

    def set_owner_user(self, domain_name, subscription_id, principal_list):
        """
        Function to get the ownership role
        :param domain_name:
        :param subscription_id:
        :param principal_list:
        :return:
        """
        access_headers = self.get_domain_access_headers('', domain_name)
        url = "https://management.azure.com/subscriptions/{}/providers/Microsoft.Authorization/roleDefinitions?" \
              "api-version=2015-07-01&$filter=roleName%20eq%20'Owner'"
        ms_url = url.format(subscription_id)

        offers_out = requests.get(ms_url, headers=access_headers)
        offers_out.encoding = 'utf-8-sig'
        offers_hash = json.loads(offers_out.text)
        result = ''
        if 'value' in offers_hash:
            for data in offers_hash['value']:
                role_id = data['id']
            result = self.set_azure_ownership(access_headers, subscription_id, principal_list, role_id)
        return result

    def set_azure_ownership(self, access_headers, subscription, principal_list, ownership_id):
        """
        Function to set ownership for azure subscription
        :param access_headers:
        :param subscription:
        :param principal_list:
        :param ownership_id:
        :return:
        """
        import uuid
        url = "https://management.azure.com/subscriptions/{}/providers/Microsoft.Authorization/roleAssignments/{}?" \
              "api-version=2015-07-01"
        if len(principal_list):
            for principal_id in principal_list:
                unique_id = str(uuid.uuid4())
                ms_url = url.format(subscription, unique_id)
                payload = {
                    "properties": {
                        "roleDefinitionId": ownership_id,
                        "principalId": principal_id
                    }
                }
                access_headers['Content-Type'] = 'application/json'
                update_ownership = requests.put(ms_url, data=json.dumps(payload), headers=access_headers)
                return update_ownership
        return False

    def get_offers(self):
        """
        Function to get list of offers from Microsoft
        :return:
        """
        offers_out = requests.get(self.base_url + 'offers?country=IN',
                                  headers=self.access_headers)
        offers_out.encoding = 'utf-8-sig'
        offers_hash = json.loads(offers_out.text)

        #offers = len(offers_hash['items'])
        #pprint("Total number of Items: %d" % (offers,))
        return offers_hash['items']

    def validate_domain_name(self, domain_name):
        """
        Function to validate the given domain name in Microsoft
        :param domain_name:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'domains/%s' % (domain_name)
        domain_request = requests.head(partner_center_url, headers=access_headers)

        if domain_request.status_code == 200:
            return True
        else:
            return False

    def get_customer_from_domain(self, domain_name):
        """
        Function to get the Customer data from given domain name
        :param domain_name:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers?filter={"Field":"Domain","Value":"%s","Operator":"starts_with"}' % domain_name
        domain_request = requests.get(partner_center_url, headers=access_headers)
        domain_request.encoding = 'utf-8-sig'
        data_to_send = customer_data = json.loads(domain_request.text)
        result = customer_data['items']
        if len(result):
            data_to_send = result[0]
        return data_to_send

    def get_order_subscriptions(self, order_id, tenant_id):
        """
        Function to get the subscription details for given order id
        :param order_id:
        :param tenant_id:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/subscriptions?order_id=%s' % (tenant_id, order_id)
        domain_request = requests.get(partner_center_url, headers=access_headers)
        domain_request.encoding = 'utf-8-sig'
        data_to_send = json.loads(domain_request.text)
        return data_to_send

    def relationship_request(self):
        """
        Function to get the Relationship request URL from Microsoft
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/relationshiprequests'
        relation_out = requests.get(partner_center_url, headers=access_headers)
        if relation_out.status_code == 200:
            relation_out.encoding = 'utf-8-sig'
            offers_hash = json.loads(relation_out.text)
            return offers_hash['url']
        else:
            return False

    def create_customer(self, payload):
        """
        Function to create Customer in Microsoft
        :param payload:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers'
        access_headers['Content-Type'] = 'application/json'
        create_customer = requests.post(partner_center_url, data=json.dumps(payload), headers=access_headers)
        if create_customer.status_code == 201:
            create_customer.encoding = 'utf-8-sig'
            customer_data = json.loads(create_customer.text)
            return customer_data
        elif create_customer.status_code == 409:
            create_customer.encoding = 'utf-8-sig'
            error_data = json.loads(create_customer.text)
            return error_data['description']
        else:
            create_customer.encoding = 'utf-8-sig'
            error_data = json.loads(create_customer.text)
            return error_data

    def create_orders(self, tenant_id, payload):
        """
        Function to place Orders in MS
        :param tenant_id:
        :param payload:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/orders' % tenant_id
        access_headers['Content-Type'] = 'application/json'
        create_order = requests.post(partner_center_url, data=json.dumps(payload), headers=access_headers)
        if create_order.status_code == 201:
            create_order.encoding = 'utf-8-sig'
            customer_data = json.loads(create_order.text)
            return customer_data
        else:
            create_order.encoding = 'utf-8-sig'
            error_data = json.loads(create_order.text)
            return error_data

    def validate_mpn_id(self, mpn_id):
        """
        Function to validate MPNID in MS
        :param mpn_id:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'profiles/mpn?mpnId=%s' % mpn_id
        mpn_request = requests.get(partner_center_url, headers=access_headers)
        if mpn_request.status_code == 200:
            return True
        else:
            return False

    def order_amendment(self, payload, tenant_id, subscription_id):
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/subscriptions/%s' % (tenant_id, subscription_id)
        access_headers['Content-Type'] = 'application/json'
        update_order = requests.patch(partner_center_url, data=json.dumps(payload), headers=access_headers)
        if update_order.status_code == 201 or update_order.status_code == 204:
            update_order.encoding = 'utf-8-sig'
            customer_data = json.loads(update_order.text)
            return customer_data
        else:
            update_order.encoding = 'utf-8-sig'
            error_data = json.loads(update_order.text)
            return error_data

    def delete_customer_from_ms(self, tenant_id):
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s' % tenant_id
        update_order = requests.delete(partner_center_url, headers=access_headers)
        if update_order.status_code == 204:
            pprint("Customer deleted : %s" % tenant_id)
        else:
            pprint("Not deleted")

    def create_user(self, tenant_id, data):
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/users' % tenant_id
        access_headers['Content-Type'] = 'application/json'
        create_user = requests.post(partner_center_url, data=json.dumps(data), headers=access_headers)
        if create_user.status_code == 201:
            create_user.encoding = 'utf-8-sig'
            customer_data = json.loads(create_user.text)
            return customer_data
        else:
            create_user.encoding = 'utf-8-sig'
            error_data = json.loads(create_user.text)
            return error_data

    def check_domain_exists(self, domain_name):
        """
        Function to check the given domain is exist in microsoft
        :param domain_name:
        :return:
        """
        partner_center_url = 'https://login.windows.net/{}/FederationMetadata/2007-06/FederationMetadata.xml'.format(
            domain_name)
        domain_request = requests.get(partner_center_url)
        return domain_request.status_code == 200

    def get_customer_subscriptions(self, tenant_id):
        """
        Function to get the subscription details for given tenant id
        :param tenant_id:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/subscriptions' % tenant_id
        domain_request = requests.get(partner_center_url, headers=access_headers)
        domain_request.encoding = 'utf-8-sig'
        data_to_send = json.loads(domain_request.text)
        return data_to_send

    def get_customer_billing_info(self, tenant_id):
        """
        Function to get the billing profile details for given tenant id
        :param tenant_id:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/profiles/billing' % tenant_id
        domain_request = requests.get(partner_center_url, headers=access_headers)
        domain_request.encoding = 'utf-8-sig'
        data_to_send = 'Failed'
        if domain_request.status_code == 200:
            data_to_send = json.loads(domain_request.text)
        return data_to_send

    def update_billing_info(self, payload, tenant_id):
        """
        Function to update the billing profile information in MPC
        :param payload:
        :param tenant_id:
        :return:
        """
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/profiles/billing' % tenant_id
        access_headers['Content-Type'] = 'application/json'
        update_customer = requests.put(partner_center_url, data=json.dumps(payload), headers=access_headers)
        if update_customer.status_code == 200 or update_customer.status_code == 204:
            update_customer.encoding = 'utf-8-sig'
            customer_data = json.loads(update_customer.text)
            return customer_data
        else:
            update_customer.encoding = 'utf-8-sig'
            error_data = json.loads(update_customer.text)
            return error_data

    def suspend_subscription(self, tenant_id, subscription):
        subscription_details = self.get_subscription_by_Id(subscription, tenant_id)
        if 'status' in subscription_details:
            if subscription_details['status'] == 'active':
                payload = self.subscription_cancel_payload(subscription_details)
                partner_center_url = self.base_url + 'customers/%s/subscriptions/%s' % (tenant_id, subscription)
                access_headers = self.access_headers
                access_headers['Content-Type'] = 'application/json'
                partner_cancel_request = requests.patch(partner_center_url, data=json.dumps(payload), headers=access_headers)
                partner_cancel_request.encoding = 'utf-8-sig'
                data_to_send = json.loads(partner_cancel_request.text)
                return data_to_send
            elif subscription_details['status'] == 'suspended':
                data_to_send ={
                    'description': 'This subscription Already Suspended'
                }
                return data_to_send
        return subscription_details
    def get_subscription_by_Id(self, subsciption_id, tenant_id):
        access_headers = self.access_headers
        partner_center_url = self.base_url + 'customers/%s/subscriptions/%s' % (tenant_id, subsciption_id)
        domain_request = requests.get(partner_center_url, headers=access_headers)
        domain_request.encoding = 'utf-8-sig'
        data_to_send = json.loads(domain_request.text)
        return data_to_send

    def subscription_cancel_payload(self, data):
        return {
            "Id": data['id'],
            "FriendlyName": data['friendlyName'],
            "Quantity": data['quantity'],
            "UnitType": "none",
            "ParentSubscriptionId": None,
            "CreationDate": data['creationDate'],
            "EffectiveStartDate": data['effectiveStartDate'],
            "CommitmentEndDate": data['commitmentEndDate'],
            "Status": "suspended",
            "AutoRenewEnabled": False,
            "BillingType": "none",
            "PartnerId": None,
            "ContractType": data['contractType'],
            "OrderId": data['orderId'],
            "Attributes": {
                "Etag": "<etag>",
                "ObjectType": "Subscription"
            }
        }

