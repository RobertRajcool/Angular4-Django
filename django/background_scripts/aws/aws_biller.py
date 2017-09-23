from awsdbrparser import config
from django.conf import settings
from elasticsearch import Elasticsearch
from billing.models import AwsBillsTransportation
import datetime
from dateutil.tz import tzlocal, tzutc
from dateutil.rrule import rrule, MONTHLY
import subprocess
import boto3
import os
import zipfile
import re
import io


class AWSBiller:
    def __init__(self):
        """ Elasticsearch configuration """

        self.config = config.Config()
        self.timezone = tzutc()

        # elasticsearch default values
        self.config.es_host = settings.ES_HOST
        self.config.es_port = settings.ES_PORT
        self.config.es_index = settings.ES_INDEX
        self.dbr_types = settings.AWS_DBR_TYPES
        self.payer_account_credentials = settings.AWS_PAYER_ACCOUNT_CREDENTIALS

    def load_to_elasticsearch(self, file_path=None):
        """ Loading given file data into elasticsearch """

        def check_dbr_type(key):
            for dbr_type in self.dbr_types:
                key_regex = re.compile(r'^[0-9]{12}-' + dbr_type[1] + r'-[0-9]{4}-[0-9]{2}.csv.zip$')
                if key_regex.search(key):
                    return True
            return False

        for trans_record in AwsBillsTransportation.objects.filter(imported=False):
            file_path = os.path.join(settings.BASE_DIR, trans_record.file.name)
            file_name, file_extension = os.path.splitext(file_path)

            if not check_dbr_type(trans_record.key):
                print("Unsupported file format: '%s'" % file_extension)
                raise FileNotFoundError("Unsupported file format: '%s'" % file_extension)
            else:
                file_key = trans_record.key
                file_key = file_key[13:len(file_key) - 16]
                dbr_type = list(filter(lambda t: t[1] == file_key, self.dbr_types))[0]

                argv = [
                    'dbrparser',
                    '-i', file_path,
                    '-to', '300',
                    '-t', '2',
                    '-bm', '2',
                    '-bs', '3000',
                    '-e', self.config.es_host,
                    '-p', self.config.es_port,
                    '-ei', '{}-{}-{}-{}'.format(self.config.es_index, dbr_type[0], trans_record.payer_account_id, trans_record.bucket),
                    '-y', str(trans_record.billing_month.year),
                    '-m', str('%02d' % trans_record.billing_month.month),
                    '--delete-index'
                ]

                python_environment = os.environ.copy()
                # python_environment["PATH"] = "/usr/sbin:/sbin:" + python_environment["PATH"]
                response = subprocess.run(argv, env=python_environment, shell=False, stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
                print(response.stdout.decode('utf-8'))

                if not response.returncode and not response.stderr:
                    trans_record.imported = True
                    trans_record.last_import = datetime.datetime.now(tz=self.timezone)
                    trans_record.save()
                else:
                    error = response.stderr.decode('utf-8')
                    raise EnvironmentError(error[len(error) - 500:])
        return 0

    def fetch_s3bills(self, beginning_date=None):
        """ Checks for new bills in s3 and downloads it """

        if not beginning_date:
            beginning_date = datetime.datetime(2017, 5, 1, tzinfo=self.timezone)

        for payer_account in self.payer_account_credentials:
            payer_account_id = payer_account.get('account_id')

            for bucket in payer_account.get('buckets'):
                bucket_name = bucket.get('bucket_name')
                credentials = {
                    "region_name": bucket.get('region_name'),
                    "aws_access_key_id": payer_account.get('aws_access_key_id'),
                    "aws_secret_access_key": payer_account.get('aws_secret_access_key')
                }

                client = boto3.client('s3', **credentials)
                response = client.list_objects(Bucket=bucket_name, Delimiter='/')
                bucket_objects_list = response['Contents']

                def check_dbr_type(key):
                    for dbr_type in self.dbr_types:
                        key_regex = re.compile(r'^[0-9]{12}-' + dbr_type[1] + r'-[0-9]{4}-[0-9]{2}.csv.zip$')
                        if key_regex.search(key):
                            return True
                    return False

                bucket_objects_list = list(
                    filter(lambda f: f['LastModified'] >= beginning_date and check_dbr_type(f['Key']),
                           bucket_objects_list))

                """ Appending bucket name on DBR filename"""

                def rename_file(filename):
                    name, ext = os.path.splitext(filename)
                    name += '-' + bucket_name
                    filename = name + ext
                    return filename

                """ Download and Parsing files """

                def download_and_parse(key):
                    storage_url = settings.AWS_BILLS_URL
                    storage_path = os.path.join(settings.BASE_DIR, settings.AWS_BILLS_URL)

                    with open('aws_detailed_bill_tmp', 'wb') as data:
                        print('Downloading file: %s ' % key)
                        client.download_fileobj(bucket_name, key, data)

                    with open('aws_detailed_bill_tmp', 'rb') as fileobj:
                        print('Parsing file: %s' % key)
                        if zipfile.is_zipfile(fileobj):
                            z = zipfile.ZipFile(fileobj)

                            for info in z.infolist():
                                info.filename = rename_file(info.filename)
                                extract_path = storage_url
                                storage_url = os.path.join(storage_url, info.filename)
                                z.extract(info, extract_path)
                            z.close()
                        else:
                            f_name = rename_file(obj['Key'])
                            storage_url = os.path.join(storage_url, f_name)
                            storage_path = os.path.join(storage_path, f_name)
                            os.rename('aws_detailed_bill_tmp', storage_path)

                    if os.path.exists('aws_detailed_bill_tmp'):
                        os.remove('aws_detailed_bill_tmp')

                    return storage_url

                for obj in bucket_objects_list:
                    end = obj['Key'].index('.') if '.' in obj['Key'] else len(obj['Key'])
                    file_name = obj['Key'][0:end]
                    fn_segments = file_name.split('-')
                    year = int(fn_segments[len(fn_segments) - 2]) if re.match(r'[0-9]{4}', fn_segments[
                        len(fn_segments) - 2]) else datetime.date.today().year
                    month = int(fn_segments[len(fn_segments) - 1]) if re.match(r'[0-9]{2}', fn_segments[
                        len(fn_segments) - 1]) else datetime.date.today().month

                    billing_month = datetime.date(year, month, 1)

                    if not AwsBillsTransportation.objects.filter(key=obj['Key'],
                                                                 bucket=bucket_name).exists():
                        """ Downloading new files """
                        url = download_and_parse(obj['Key'])
                        trans_record = AwsBillsTransportation.objects.create(
                            payer_account_id=payer_account_id,
                            key=obj['Key'],
                            bucket=bucket_name,
                            billing_month=billing_month,
                            last_bill_update=obj['LastModified'],
                            file=url,
                            last_download=datetime.datetime.now(tz=self.timezone)
                        )
                        trans_record.save()
                    else:
                        """ Updating existing files """
                        trans_record = AwsBillsTransportation.objects.filter(key=obj['Key'],
                                                                             bucket=bucket_name).first()
                        if obj['LastModified'] > trans_record.last_bill_update:
                            url = download_and_parse(obj['Key'])
                            trans_record.imported = False
                            trans_record.billing_month = billing_month
                            trans_record.last_bill_update = obj['LastModified']
                            trans_record.file = url
                            trans_record.last_download = datetime.datetime.now(tz=self.timezone)
                            trans_record.save()

        return AwsBillsTransportation.objects.filter(imported=False)

    def fetch_consolidated_bill(self, **params):
        """ Generating consolidated bill for provided details """
        """
            valid params:
                from - datetime object, required, default: current month start
                to - datetime object, required, default: current month end
                customer_account_ids - list, optional, default: all
                size - integer, optional, default: 5
                invoiced - boolean, optional , default: False
                extra_indices - list, optional
        """
        es = Elasticsearch(hosts=[settings.ES_HOST], port=settings.ES_PORT, timeout=120)

        months = [mon for mon in
                  rrule(MONTHLY, dtstart=params['from'].replace(day=1), until=params['to'].replace(day=1))]
        # previous_of_start_date = params['from'] - datetime.timedelta(days=1)

        # if months[0].month != previous_of_start_date.month:
        #     months.insert(0, previous_of_start_date)

        # Selecting indices for searching
        payer_accounts = self.payer_account_credentials
        indices = list()
        for mon in months:
            for dbr_type in self.dbr_types:
                for payer_acc in payer_accounts:
                    for bucket in payer_acc['buckets']:
                        indices.append(
                            '%s-%s-%s-%s-%04d-%02d' % (
                                self.config.es_index,
                                dbr_type[0],
                                payer_acc['account_id'],
                                bucket['bucket_name'],
                                mon.year,
                                mon.month
                            )
                        )

        if 'extra_indices' in params and isinstance(params['extra_indices'], list):
            indices += params['extra_indices']

        indices = list(filter(lambda indice: es.indices.exists(indice), indices))

        # Constructing search query
        query = dict()
        # params["to"] = (params["to"] + datetime.timedelta(days=1)) - datetime.timedelta(milliseconds=1)

        range_query = {
            "UsageStartDate": {
                "gte": datetime.datetime.strftime(params["from"], "%Y-%m-%d %H:%M:%S"),
                "lte": datetime.datetime.strftime(params["to"], "%Y-%m-%d %H:%M:%S")
            }
        }

        # Rounding off month
        if params['round_off_month']:
            range_query['UsageStartDate'].pop('lte', None)

        query["size"] = 0
        query["query"] = {
            "bool": {
                "must": [
                    {  # Date range filter
                        "bool": {
                            "should": [
                                {
                                    "range": range_query
                                }
                            ]
                        }
                    }
                ]
            }
        }

        if params.get('invoiced', False):
            query["query"]["bool"]["must_not"] = {
                "term": {
                    "InvoiceID": "Estimated"
                }
            }

        # Filtering by customer account id
        if params["customer_account_ids"] is not None:
            customer_account_query = {"should": []}
            for account_id in params["customer_account_ids"]:
                customer_account_query["should"].append({"term": {"LinkedAccountId": account_id}})

            query["query"]["bool"]["must"].append({"bool": customer_account_query})

        # Grouping queries
        query["aggs"] = {  # Grouping by payer accounts
            "payers": {
                "terms": {"field": "PayerAccountId", "size": 15},
                "aggs": {  # Grouping by customers
                    "customers": {
                        "terms": {"field": "LinkedAccountId", "size": params['size']},
                        "aggs": {  # Grouping by products
                            "products": {
                                "terms": {"field": "ProductName", "size": 200},
                                "aggs": {  # Grouping by regions
                                    "regions": {
                                        "terms": {"field": "Region", "size": 30},
                                        "aggs": {  # Grouping by usage types
                                            "usage_types": {
                                                "terms": {"field": "UsageType", "size": 500},
                                                "aggs": {
                                                    "item_descriptions": {
                                                        "terms": {"field": "ItemDescription", "size": 500},
                                                        "aggs": {
                                                            "invoice_ids": {
                                                                "terms": {"field": "InvoiceID"},
                                                                "aggs": {  # Grouping by ItemDescription
                                                                    "balance": {
                                                                        "filter": {
                                                                            "range": {"UnBlendedCost": {"gte": 0}}
                                                                        },
                                                                        "aggs": {  # Balance calculations
                                                                            "invoice_id_total_usage": {
                                                                                # Sum of usage of individual invoice id
                                                                                "sum": {"field": "UsageQuantity"}
                                                                            },
                                                                            "invoice_id_total_blended_cost": {
                                                                                # Sum of blended cost of individual invoice id
                                                                                "sum": {"field": "BlendedCost"}
                                                                            },
                                                                            "invoice_id_total_unblended_cost": {
                                                                                # Sum of unblended cost of individual invoice id
                                                                                "sum": {"field": "UnBlendedCost"}
                                                                            },
                                                                        }
                                                                    },
                                                                    "credits": {
                                                                        "filter": {
                                                                            "range": {"UnBlendedCost": {"lt": 0}}
                                                                        },
                                                                        "aggs": {  # Credit calculations
                                                                            "invoice_id_total_usage": {
                                                                                # Sum of usage of individual invoice id
                                                                                "sum": {"field": "UsageQuantity"}
                                                                            },
                                                                            "invoice_id_total_blended_cost": {
                                                                                # Sum of blended credit of individual invoice id
                                                                                "sum": {"field": "BlendedCost"}
                                                                            },
                                                                            "invoice_id_total_unblended_cost": {
                                                                                # Sum of unblended credit of individual invoice id
                                                                                "sum": {"field": "UnBlendedCost"}
                                                                            },
                                                                        }
                                                                    },
                                                                    "fields": {  # Collecting fields
                                                                        "top_hits": {
                                                                            "_source": {
                                                                                "include": [
                                                                                    "UsageStartDate",
                                                                                    "UsageEndDate",
                                                                                    "SubscriptionId",
                                                                                    "ItemDescription",
                                                                                    "Operation",
                                                                                    "RateId",
                                                                                    "PricingPlanId",
                                                                                    "BlendedRate",
                                                                                    "UnBlendedRate",
                                                                                    "ReservedInstance",
                                                                                    "RecordId",
                                                                                    "InvoiceID"
                                                                                ]
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "usage_type_total_usage": {
                                                        # Sum of usage of individual usage type
                                                        "sum": {"field": "UsageQuantity"}
                                                    },
                                                    "usage_type_total_blended_cost": {
                                                        # Sum of blended cost of individual usage type
                                                        "sum": {"field": "BlendedCost"}
                                                    },
                                                    "usage_type_total_unblended_cost": {
                                                        # Sum of unblended cost of individual usage type
                                                        "sum": {"field": "UnBlendedCost"}
                                                    },
                                                }

                                            },
                                            "region_total_usage": {  # Sum of usage of individual region
                                                "sum": {"field": "UsageQuantity"}
                                            },
                                            'region_total_unblended_cost': {  # Sum of blended cost of individual region
                                                "sum": {"field": "UnBlendedCost"}
                                            },
                                            'region_total_blended_cost': {  # Sum of blended cost of individual region
                                                "sum": {"field": "BlendedCost"}
                                            }
                                        }
                                    },
                                    "fields": {  # Pricing plan id grouping source
                                        "top_hits": {
                                            "_source": {
                                                "include": [
                                                    "ProductName",
                                                    "PricingPlanId"
                                                ]
                                            }
                                        }
                                    },
                                    "product_total_usage": {  # Sum of usage of individual product
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    'product_total_unblended_cost': {  # Sum of blended cost of individual product
                                        "sum": {"field": "UnBlendedCost"}
                                    },
                                    'product_total_blended_cost': {  # Sum of blended cost of individual product
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            },
                            "linked_account_total_usage": {  # Sum of usage of individual linked account id
                                "sum": {"field": "UsageQuantity"}
                            },
                            "linked_account_total_unblended_cost": {
                                # Sum of blended cost of individual linked account id
                                "sum": {"field": "UnBlendedCost"}
                            },
                            "linked_account_total_blended_cost": {
                                # Sum of blended cost of individual linked account id
                                "sum": {"field": "BlendedCost"}
                            },
                            # Reserved instance summary
                            "reserved_instance_summary": {
                                "filter": {
                                    "term": {"ReservedInstance": "Y"}
                                },
                                "aggs": {
                                    "total_usage": {
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    "total_unblended_cost": {
                                        "sum": {"field": "UnBlendedCost"}
                                    }, "total_blended_cost": {
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            },
                            # AWS business support summary
                            "aws_business_support_summary": {
                                "filter": {
                                    "term": {"ProductName": "AWS Support (Business)"}
                                },
                                "aggs": {
                                    "total_usage": {
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    "total_unblended_cost": {
                                        "sum": {"field": "UnBlendedCost"}
                                    }, "total_blended_cost": {
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            },
                            # AWS developer support summary
                            "aws_developer_support_summary": {
                                "filter": {
                                    "term": {"ProductName": "AWS Support (Developer)"}
                                },
                                "aggs": {
                                    "total_usage": {
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    "total_unblended_cost": {
                                        "sum": {"field": "UnBlendedCost"}
                                    }, "total_blended_cost": {
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            },
                            # AWS all other regular products summary
                            "regular_products_summary": {
                                "filter": {
                                    "bool": {
                                        "must_not": [
                                            {"term": {"ReservedInstance": "Y"}},
                                            {"term": {"ProductName": "AWS Support (Business)"}},
                                            {"term": {"ProductName": "AWS Support (Developer)"}},
                                            {"term": {"ProductName": ""}}
                                        ]
                                    }
                                },
                                "aggs": {
                                    "total_usage": {
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    "total_unblended_cost": {
                                        "sum": {"field": "UnBlendedCost"}
                                    },
                                    "total_blended_cost": {
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            },
                            # Unknown
                            "unknown": {
                                "filter": {
                                    "bool": {
                                        "must": [
                                            {"term": {"ProductName": ""}}
                                        ]
                                    }
                                },
                                "aggs": {
                                    "total_usage": {
                                        "sum": {"field": "UsageQuantity"}
                                    },
                                    "total_unblended_cost": {
                                        "sum": {"field": "UnBlendedCost"}
                                    },
                                    "total_blended_cost": {
                                        "sum": {"field": "BlendedCost"}
                                    }
                                }
                            }

                        }
                    }
                }
            }
        }

        # Request to elasticsearch
        result = es.search(
            index=','.join(indices),
            body=query
        )
        return result
