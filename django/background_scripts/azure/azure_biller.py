from django.conf import settings
import datetime
from dateutil.tz import tzlocal, tzutc
from dateutil.relativedelta import relativedelta
import pandas
import numpy
import os


class AZUREBiller:
    billing_cycle_start_day = 22

    def __init__(self, **kwargs):
        """ Configurations """

        self.timezone = tzutc()
        self.reconciliation_files_root = \
            kwargs['file_path'] if 'file_path' in kwargs else 'billing/azure_bills/consolidated'
        self.reconciliation_filename_regex = 'Redington (India) Limited_IND_SRR_{}23_usagebased-{}'
        self.reconciliation_filename_extension = '.xlsx'

        today = datetime.date.today()
        self.billing_month = (today + relativedelta(months=1)).replace(day=1) \
            if today.day >= self.billing_cycle_start_day \
            else today.replace(day=1)

        self.reconciliation_filename = None
        self.invoice_number = 'invalid_invoice_number'
        self.custom_reconciliation_filename = None
        self.reconciliation_data = None

    def fetch_bill(self, **params):
        """ Generating consolidated bill for provided details """
        """
            valid params:
                month - billing month, default: current month
                to - datetime object, required, default: current month end
                customer_tenant_ids (tenant ids) - list, optional, default: []
        """

        self.update_constants(params=params)

        filters = {
            'billing_month': self.billing_month,
            'customer_tenant_ids': list()
        }

        params['billing_month'] = params['billing_month'].replace(day=1)

        filters.update(params)

        if self.reconciliation_data is None or self.billing_month != filters['billing_month']:
            self.billing_month = filters['billing_month']
            self.read_file_data()

        if len(filters['customer_tenant_ids']) == 0:
            raise ValueError('No customer tenant id provided')
        else:
            filters['customer_tenant_ids'] = list(map(lambda t: t.lower(), filters['customer_tenant_ids']))

        """ Applying Filters """
        reco_dataframe = self.reconciliation_data
        result = reco_dataframe[
            (reco_dataframe['CustomerId'].str.lower().isin(filters['customer_tenant_ids']))
            # & (reco_dataframe['ChargeEndDate'] >= filters['from'])
            # & (reco_dataframe['ChargeEndDate'] <= filters['to'])
        ]

        result = result.to_dict(orient='records')
        return result

    def read_file_data(self):
        """ Reading date from excel file """

        if self.custom_reconciliation_filename:
            self.reconciliation_filename = self.custom_reconciliation_filename
        else:
            self.reconciliation_filename = self.reconciliation_filename_regex.format(
                self.billing_month.strftime('%Y%m'),
                self.invoice_number
            )

        reconciliation_file_path = os.path.join(self.reconciliation_files_root,
                                                self.reconciliation_filename +
                                                self.reconciliation_filename_extension)

        """ Check if file is exists """
        if not os.path.exists(reconciliation_file_path):
            raise FileNotFoundError('Reconciliation file not found in : %s' % reconciliation_file_path)

        self.reconciliation_data = pandas.read_excel(reconciliation_file_path,
                                                     sheetname=self.reconciliation_filename,
                                                     header=0).fillna('')

        def convert_dtype(column_name, dtype):
            """ Data type converter """
            if column_name not in self.reconciliation_data.columns:
                return False
            if dtype == 'datetime':
                self.reconciliation_data[column_name] = pandas.to_datetime(self.reconciliation_data[column_name])

        """ Refactoring data types """
        dtypes = {
            'ChargeStartDate': 'datetime',
            'ChargeEndDate': 'datetime'
        }

        for column, d_type in dtypes.items():
            convert_dtype(column_name=column, dtype=d_type)

        return True

    def update_constants(self, params):
        self.custom_reconciliation_filename = params.get('file_name', None)
        self.invoice_number = params.get('invoice_number', self.invoice_number)
