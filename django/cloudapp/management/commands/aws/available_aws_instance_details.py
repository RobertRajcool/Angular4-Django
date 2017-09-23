import os.path
import datetime
from django.db.models import Q
from redington.settings import AWS_CREDENTIALS, BASE_DIR
from cloudtemplates.runner import EC2Runner
from products.models import VendorDetails, Products
from cloudtemplates.models import CloudInstances
from customers.models import CloudAccounts, Customers
from cloudtemplates.tasks import get_payer_account


class AvailableAwsInstanceDetails:
    AWS_JBA = 'AWSC'
    playbook = os.path.join(BASE_DIR, 'playbooks', 'aws/refresh_instance.yml')

    def __init__(self, partner):
        '''
        This is the initial function of this class
        Through which function only all the actions to be performed
        '''
        self.partner = partner

    def perform_actions(self):
        '''
        Function to perform actions to gather available instance details and update it into database
        :return:
        '''
        for instance in self.get_available_instances():
            print('%s - %s updating started...' % (instance.name, instance.instance_id))
            try:
                self.run_ansible_playbook(instance)
            except Exception:
                # TODO: Need to do exception handling
                print('%s - %s update: exception occurred!' % (instance.name, instance.instance_id))
                continue

    def run_ansible_playbook(self, instance):
        '''
        Function to execute ansible playbook to get instance details
        instance is dict which refers to created instance details
        :param instance:
        :return:
        '''
        runner = EC2Runner('Store Output')
        extra_variables = {
            'tenantAccountId': self.get_customer_tenant_account(instance.customer_id),
            'region': instance.region,
            'instance_id': instance.instance_id,
            'group_name': instance.security_details[0]['group_name'] if instance.security_details else
            instance.name+'_sg'
        }
        status, results = runner.get_results(self.playbook, AWS_CREDENTIALS[get_payer_account(instance.customer_id)],
                                             extra_variables)
        if status:
            self.update(instance.id, results['results'])
        else:
            # TODO: Need to handle run playbook failure
            print('%s - %s update: run playbook failed!' % (instance.name, instance.instance_id))

    def update(self, instance, result):
        '''
        Function to update gathered instance details into database
        instance is number which refers to instance id
        result is dict which refers to gathered information after running the ansible playbook
        :param instance:
        :param result:
        :return:
        '''
        self.update_instance_details(instance, result[0]['group_facts']['instances'],
                                     result[1]['security_facts']['security_groups'])
        # self.update_security_details(instance, result[1]['security_facts']['security_groups'])

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
        if len(result) > 0 :
            result = result[0]
            CloudInstances.objects.filter(id=instance).update(instance_id=result['id'], state=result['state'],
                                                              ip_address=result['public_ip_address'],
                                                              instance_details=result, security_details=firewall,
                                                              last_synched_date=datetime.datetime.now())
            print('%s - %s updated successfully' % (CloudInstances.objects.get(pk=instance).name,
                                                    CloudInstances.objects.get(pk=instance).instance_id))
        else:
            print('%s - %s is terminated. Deleted from database!' % (
                CloudInstances.objects.get(pk=instance).name, CloudInstances.objects.get(pk=instance).instance_id))
            self.remove_terminated_instance(instance)

    def update_security_details(self, instance, result):
        '''
        Function to update gathered instance details into database
        instance is number which refers to instance id
        result is dict which refers to gathered information of security details after running the ansible playbook
        :param instance:
        :param result:
        :return:
        '''
        CloudInstances.objects.filter(id=instance).update(security_details=result)

    def remove_terminated_instance(self, instance):
        '''
        Function to remove terminated instance
        instance is number which refers to instance id
        :param instance:
        :return:
        '''
        CloudInstances.objects.filter(pk=instance).delete()

    def get_customer_tenant_account(self, customer):
        '''
        Function to get customer cloud account details
        customer is number which refers to the customer id
        :param customer:
        :return:
        '''
        return CloudAccounts.objects.filter(Q(customer_id=customer), Q(type='AWS')).first().details['account_id']

    def get_aws_vendor(self):
        '''
        Function to get AWS vendor id
        :return:
        '''
        return VendorDetails.objects.get(vendor_jbareference=self.AWS_JBA).vendor_id

    def get_aws_products(self):
        '''
        Function to get all AWS products available
        :return:
        '''
        return Products.objects.filter(vendor_details_id=self.get_aws_vendor()).values_list('prod_id', flat=True)

    def get_customers_based_on_partner(self):
        """
        Function to get all customers based on partner
        :return:
        """
        return Customers.objects.filter(partner_id=self.partner).values_list('id', flat=True)

    def get_available_instances(self):
        '''
        Function to get all AWS created instances
        :return:
        '''
        filters = dict()
        filters['product_id__in'] = self.get_aws_products()
        filters['customer_id__in'] = self.get_customers_based_on_partner()

        return CloudInstances.objects.filter(**filters)


