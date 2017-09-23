import os.path
import datetime
from django.db.models import Q
from redington.settings import AZURE_CREDENTIALS, BASE_DIR
from cloudtemplates.runner import AzureComputeRunner
from products.models import VendorDetails, Products
from cloudtemplates.models import CloudInstances
from customers.models import CloudAccounts, Customers
from orders.models import Subscriptions


class AvailableAzureInstanceDetails:
    AZURE_JBA = 'MSCL'
    playbook = os.path.join(BASE_DIR, 'playbooks', 'azure/azure_refresh.yml')

    def __init__(self, partner):
        """
        This is the constructor of this class
        partner is number which refers to the partner id
        """
        self.partner = partner

    def perform_actions(self):
        """
        Function to perform actions to gather available instance details and update it into database
        :return:
        """
        for instance in self.get_available_instances():
            print('%s - %s updating started...' % (instance.name, instance.instance_id))
            try:
                self.run_ansible_playbook(instance)
            except Exception:
                # TODO: Need to do exception handling
                print('%s - %s update: exception occurred!' % (instance.name, instance.instance_id))
                continue

    def run_ansible_playbook(self, instance):
        """
        Function to execute ansible playbook to get instance details
        instance is dict which refers to created instance details
        :param instance:
        :return:
        """
        runner = AzureComputeRunner('Store Output')
        extra_variables = {
            'tenantId': self.get_customer_tenant_account(instance.customer_id),
            'subscriptionId': self.get_customers_subscription(instance.customer_id),
            'region': instance.region,
            'name': instance.instance_id,
        }
        status, results = runner.get_results(self.playbook, AZURE_CREDENTIALS, extra_variables)
        if status:
            self.update(instance.id, results['results'])
        else:
            # TODO: Need to handle run playbook failure
            print('%s - %s update: run playbook failed!' % (instance.name, instance.instance_id))

    def update(self, instance, result):
        """
        Function to update gathered instance details into database
        instance is number which refers to instance id
        result is dict which refers to gathered information after running the ansible playbook
        :param instance:
        :param result:
        :return:
        """
        self.update_instance_details(instance, result[1]['vm_facts']['ansible_facts']['azure_vm'],
                                     result[0]['security_facts']['ansible_facts']['azure_securitygroups'])

    def update_instance_details(self, instance, result, firewall):
        '''
        Function to update gathered instance details into database
        instance is number which refers to instance id
        result is dict which refers to gathered information of instance details after running the ansible playbook
        firewall is dict which refers to gathered information of firewall details
        :param instance:
        :param result:
        :param firewall:
        :return:
        '''
        if len(result) > 0:
            # result = result[0]
            ip_address = result['properties']['networkProfile']['networkInterfaces'][0]['properties'][
                'ipConfigurations'][0]['properties']['publicIPAddress']['properties']['ipAddress']
            CloudInstances.objects.filter(id=instance).update(instance_id=result['name'], state=result['powerstate'],
                                                              ip_address=ip_address,
                                                              instance_details=result, security_details=firewall,
                                                              last_synched_date=datetime.datetime.now())
            print('%s - %s updated successfully' % (CloudInstances.objects.get(pk=instance).name,
                                                    CloudInstances.objects.get(pk=instance).instance_id))
        else:
            print('%s - %s is terminated. Deleted from database!' % (
                CloudInstances.objects.get(pk=instance).name, CloudInstances.objects.get(pk=instance).instance_id))
            self.remove_terminated_instance(instance)

    def remove_terminated_instance(self, instance):
        '''
        Function to remove terminated instance
        instance is number which refers to instance id
        :param instance:
        :return:
        '''
        CloudInstances.objects.filter(pk=instance).delete()

    def get_customer_tenant_account(self, customer):
        """
        Function to get customer cloud account details
        customer is number which refers to the customer id
        :param customer:
        :return:
        """
        return CloudAccounts.objects.get(Q(customer_id=customer), Q(type='MS')).details['tenant_id']

    def get_customers_subscription(self, customer):
        """
        Function to get the subscription
        customer is number which refers to the customer id
        :param customer:
        :return:
        """
        filters = dict()
        filters['product_id__in'] = self.get_azure_products()
        filters['customer_id'] = customer

        return Subscriptions.objects.get(**filters).subscription

    def get_azure_vendor(self):
        """
        Function to get Azure vendor id
        :return:
        """
        return VendorDetails.objects.filter(vendor_jbareference=self.AZURE_JBA).first().vendor_id

    def get_azure_products(self):
        """
        Function to get all Azure products available
        :return:
        """
        return Products.objects.filter(vendor_details_id=self.get_azure_vendor()).values_list('prod_id', flat=True)

    def get_customers_based_on_partner(self):
        """
        Function to get all customers based on partner
        :return:
        """
        return Customers.objects.filter(partner_id=self.partner).values_list('id', flat=True)

    def get_available_instances(self):
        """
        Function to get all Azure created instances
        :return:
        """
        filters = dict()
        filters['product_id__in'] = self.get_azure_products()
        filters['customer_id__in'] = self.get_customers_based_on_partner()

        return CloudInstances.objects.filter(**filters)
