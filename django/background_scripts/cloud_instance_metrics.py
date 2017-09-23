from cloudtemplates.models import CloudInstances, InstanceMetrics, InstanceMetricsRuns
from cloudapp.defaults import AppDefaults
from cloudtemplates.tasks import AWS_AUTH, AZURE_AUTH
from orders.models import Subscriptions
import requests

from datetime import timedelta
import datetime
import boto3

MSFT_PASSWORD_CLIENT_ID = '04b07795-8ddb-461a-bbee-02f9e1bf7b46'        # Web Auth client id

class CloudInstanceMetrics:
    def __init__(self, partner):
        self.partner = partner

    def get_metrics(self):
        instances = CloudInstances.objects.filter(deleted = 0, customer__in = self.partner.customers_set.all())
        for instance in instances:

            if instance.product.vendor_details.vendor_name == AppDefaults.cloud_vendor_codes(return_as='name',
                                                                                       query_str='AWS'):
                cloudaccount = instance.customer.cloud_accounts.filter(type = 'AWS').first()
                # AWS Instance
                sts = boto3.client('sts',
                                   aws_access_key_id=AWS_AUTH['AWS_ACCESS_KEY'],
                                   aws_secret_access_key=AWS_AUTH['AWS_SECRET_KEY'],
                                   region_name=instance.region)
                role_details = sts.assume_role(
                    RoleArn=str.format('arn:aws:iam::{}:role/ec2_crossrole', cloudaccount.details['account_id']),
                    RoleSessionName='sts_access')
                credentials = role_details['Credentials']
                cloudwatch = boto3.client('cloudwatch',
                                          aws_access_key_id=credentials['AccessKeyId'],
                                          aws_secret_access_key=credentials['SecretAccessKey'],
                                          aws_session_token=credentials['SessionToken'],
                                          region_name=instance.region)

                # Check the last run for the various metrics
                metrics = ['CPUUtilization', 'DiskReadBytes', 'DiskWriteBytes', 'NetworkIn', 'NetworkOut']
                for metric in metrics:
                    instance_metric_run = InstanceMetricsRuns.objects.filter(instance = instance, metrics_type=metric)
                    start_Time = None
                    if instance_metric_run.count() == 0:
                        # First run
                        start_Time = datetime.datetime.now() - timedelta(days=1)
                    else:
                        start_Time = instance_metric_run[0].last_run

                    endTime = datetime.datetime.now()

                    response = cloudwatch.get_metric_statistics(Namespace = 'AWS/EC2',
                                                     MetricName = metric,
                                                     Dimensions = [
                                                        {
                                                            'Name': 'InstanceId',
                                                            'Value': instance.instance_id
                                                        }
                                                     ],
                                                     StartTime=start_Time,
                                                     EndTime=endTime,
                                                     Period=300,
                                                     Statistics=['Average']
                                                     )

                    for datapoint in response['Datapoints']:
                        instancemetrics = InstanceMetrics()
                        instancemetrics.instance = instance
                        instancemetrics.vendor_type = instance.product.vendor_details.vendor_id
                        instancemetrics.metrics_type = metric
                        instancemetrics.value = datapoint['Average']
                        instancemetrics.time_stamp = datapoint['Timestamp']
                        instancemetrics.save()

                    if instance_metric_run.count() == 0:
                        InstanceMetricsRuns.objects.create(
                            instance = instance,
                            vendor_type = instance.product.vendor_details.vendor_id,
                            metrics_type = metric,
                            last_run = endTime
                        )
                    else:
                        instance_metric = instance_metric_run[0]
                        instance_metric.last_run = endTime
                        instance_metric.save()

            elif instance.product.vendor_details.vendor_name == AppDefaults.cloud_vendor_codes(return_as='name',
                                                                                       query_str='MS'):
                cloudaccount = instance.customer.cloud_accounts.filter(type='MS').first()
                # Azure
                tenant_id = cloudaccount.details['tenant_id']
                subscription = Subscriptions.objects.filter(customer=instance.customer, name = 'Microsoft Azure', status = 'active')
                if subscription.count() == 0:
                    return      # TODO: Inform that there is no subscription
                elif not tenant_id:
                    return      # TODO: Inform that there is no subscription

                subscription_id = subscription[0].subscription
                metrics = ['Percentage CPU', 'Network In', 'Network Out', 'Disk Read Bytes', 'Disk Write Bytes']
                instance_id = instance.instance_details['id']

                login_url = str.format('https://login.windows.net/{}/oauth2/token', tenant_id)
                auth_params = {
                    'grant_type': 'password',
                    'client_id': MSFT_PASSWORD_CLIENT_ID,
                    'scope': 'openid',
                    'resource': 'https://management.azure.com/',
                    'username': AZURE_AUTH['AZURE_AD_USER'],
                    'password': AZURE_AUTH['AZURE_PASSWORD']
                }

                auth = requests.post(login_url, auth_params)

                if auth.status_code == 200:
                    auth_json = auth.json()
                    auth_token = auth_json['access_token']

                    for metric in metrics:
                        instance_metric_run = InstanceMetricsRuns.objects.filter(instance=instance, metrics_type=metric)
                        startTime = datetime.datetime.utcnow()
                        startTime_string = None
                        if instance_metric_run.count() == 0:
                            # First run ((1 day from today
                            startTime = startTime + timedelta(days=-1)
                            startTime_string = startTime.strftime('%Y-%m-%dT%H:%M:%SZ')
                        else:
                            startTime = instance_metric_run[0].last_run
                            startTime_string = startTime.strftime('%Y-%m-%dT%H:%M:%SZ')

                        endTime = datetime.datetime.utcnow()
                        endTime_string = endTime.strftime('%Y-%m-%dT%H:%M:%SZ')

                        metric_url = str.format('https://management.azure.com/{}/providers/microsoft.insights/metrics', instance_id)
                        metric_url_query_params = {
                            'api-version': '2016-09-01',
                            '$filter': str.format("name.value eq '{}' and aggregationType eq 'Average' and startTime eq {} and endTime eq {} and timeGrain eq duration'PT5M'", metric, startTime_string, endTime_string)
                        }

                        metrics_output = requests.get(metric_url, params=metric_url_query_params, headers = {
                            'Accept': 'application/json',
                            'Authorization': 'Bearer %s' %(auth_token,)
                        })
                        if metrics_output.status_code == 200:
                            metrics_out = metrics_output.json()
                            datapoints = metrics_out['value'][0]['data']
                            for datapoint in datapoints:
                                instancemetrics = InstanceMetrics()
                                instancemetrics.instance = instance
                                instancemetrics.vendor_type = instance.product.vendor_details.vendor_id
                                instancemetrics.metrics_type = metric
                                instancemetrics.value = datapoint.get('average',0)
                                instancemetrics.time_stamp = datapoint['timeStamp']
                                instancemetrics.save()

                            if instance_metric_run.count() == 0:
                                InstanceMetricsRuns.objects.create(
                                    instance=instance,
                                    vendor_type=instance.product.vendor_details.vendor_id,
                                    metrics_type=metric,
                                    last_run=endTime
                                )
                            else:
                                instance_metric = instance_metric_run[0]
                                instance_metric.last_run = endTime
                                instance_metric.save()

                        else:
                            print("Error Fetching metrics, Investigate")
                            continue
                else:
                    print("Error authenticating to Domain: %s" %(tenant_id,))
                    return          #TODO: Inform about the failure
