from collections import OrderedDict

reportHash = dict()


class ReportFieldMapping():
    # database modal mappings
    def __init__(self):
        # product field Mapping Options
        product_field_options = OrderedDict()
        product_field_options['product_sku_code'] = 'SKU Code'
        product_field_options['product_name'] = 'Product Name'
        product_field_options['vendor_name'] = 'Vendor'
        product_field_options['product_billing_type'] = 'Billing Type(per)'
        product_field_options['product_jbacode'] = 'JBA Code'
        product_field_options['unit_cost_currecny'] = 'UnitCost'
        product_field_options['unit_price_currecny'] = 'UnitPrice'
        product_field_options['standard_discount'] = 'Discount(%)'

        # inactive partner filed Mapping Options
        in_active_partner_filed_options = OrderedDict()
        in_active_partner_filed_options['company_name'] = 'Company name'
        in_active_partner_filed_options['mobile'] = 'Mobile'
        in_active_partner_filed_options['email'] = 'Email'
        in_active_partner_filed_options['city'] = 'City'
        in_active_partner_filed_options['state'] = 'State'
        in_active_partner_filed_options['pin_code'] = 'Pin Code'
        in_active_partner_filed_options['created_at'] = 'Reg Date'
        in_active_partner_filed_options['existing_status'] = 'Ext Partner'
        in_active_partner_filed_options['preferred_user_name'] = 'Username'
        in_active_partner_filed_options['partner_type'] = 'Partner Type'
        in_active_partner_filed_options['business_type'] = 'Business Type'
        in_active_partner_filed_options['focused_customer'] = 'Focused customer vertical'
        in_active_partner_filed_options['interested_workload'] = 'Interested workloads to work with Redington'
        in_active_partner_filed_options['credits'] = 'Credit limit'

        # active partner filed Mapping Options
        active_partner_filed_options = OrderedDict()
        active_partner_filed_options['company_name'] = 'Company name'
        active_partner_filed_options['jba_code'] = 'JBA Code'
        active_partner_filed_options['mobile'] = 'Mobile'
        active_partner_filed_options['email'] = 'Email'
        active_partner_filed_options['city'] = 'City'
        active_partner_filed_options['state'] = 'State'
        active_partner_filed_options['pin_code'] = 'Pin Code'
        active_partner_filed_options['created_at'] = 'Reg Date'
        active_partner_filed_options['existing_status'] = 'Ext Partner'
        active_partner_filed_options['user_name'] = 'Username'
        active_partner_filed_options['partner_type'] = 'Partner Type'
        active_partner_filed_options['business_type'] = 'Business Type'
        active_partner_filed_options['focused_customer'] = 'Focused customer vertical'
        active_partner_filed_options['interested_workload'] = 'Interested workloads to work with Redington'
        active_partner_filed_options['credits'] = 'Credit limit'
        active_partner_filed_options['email_1'] = 'Secondary Email'
        active_partner_filed_options['email_2'] = 'Secondary Email2'
        active_partner_filed_options['email_3'] = 'Seconary Email3'

        rejected_partner_filed_options = OrderedDict()
        rejected_partner_filed_options['company_name'] = 'Company name'
        rejected_partner_filed_options['jba_code'] = 'JBA Code'
        rejected_partner_filed_options['mobile'] = 'Mobile'
        rejected_partner_filed_options['email'] = 'Email'
        rejected_partner_filed_options['city'] = 'City'
        rejected_partner_filed_options['state'] = 'State'
        rejected_partner_filed_options['pin_code'] = 'Pin Code'
        rejected_partner_filed_options['created_at'] = 'Reg Date'
        rejected_partner_filed_options['existing_status'] = 'Ext Partner'
        rejected_partner_filed_options['partner_type'] = 'Partner Type'
        rejected_partner_filed_options['business_type'] = 'Business Type'
        rejected_partner_filed_options['focused_customer'] = 'Focused customer vertical'
        rejected_partner_filed_options['interested_workload'] = 'Interested workloads to work with Redington'
        rejected_partner_filed_options['credits'] = 'Credit limit'
        rejected_partner_filed_options['email_1'] = 'Secondary Email'
        rejected_partner_filed_options['email_2'] = 'Secondary Email2'
        rejected_partner_filed_options['email_3'] = 'Seconary Email3'

        # File Export field mappings for customer cloud accounts
        reportHash['customer_aws_accounts_list'] = OrderedDict(CUSTOMER_AWS_ACCOUNTS_FIELDS)

        # File Export field mappings for aws sales orders
        reportHash['aws_sales_orders_list'] = OrderedDict(AWS_SALES_ORDER_FIELDS)

        # File Export field mappings for pending requests
        reportHash['pending_requests_list'] = OrderedDict(PENDING_REQUESTS_FIELDS)

        # File Export field mappings for aws orders report
        reportHash['aws_orders_report'] = OrderedDict(AWS_ORDERS_REPORT)

        reportHash['productList'] = product_field_options
        reportHash['in_active_partner_list'] = in_active_partner_filed_options
        reportHash['active_partner_list'] = active_partner_filed_options
        reportHash['aws_active_partner_list'] = OrderedDict(ACTIVE_AWS_PARTERS_FIELDS)
        reportHash['tranasacting_partner_reports'] =OrderedDict(TRANSACTING_PARTNER_REPORT)
        reportHash['customer_segmentation_reports'] =OrderedDict(CUSTOMER_SEGMENTATION_REPORT)
        reportHash['rejected_partner_list'] = rejected_partner_filed_options

    def createReport(self, hash_key_value):
        try:
            return reportHash[hash_key_value]
        except:
            return None


ACTIVE_AWS_PARTERS_FIELDS = (
    ('apn_id', 'APN id'),
    ('company_name', 'Company name'),
    ('jba_code', 'JBA code'),
    ('mobile', 'Mobile'),
    ('email', 'Email'),
    ('city', 'City'),
    ('state', 'State'),
    ('pin_code', 'Pin Code'),
    ('created_at', 'Reg Date'),
    ('existing_status', 'Ext Partner'),
    ('user_name', 'Username'),
    ('partner_type', 'Partner Type'),
    ('business_type', 'Business Type'),
    ('focused_customer', 'Focused customer vertical'),
    ('interested_workload', 'Interested workloads to work with Redington'),
    ('credits', 'Credit limit')
)
CUSTOMER_AWS_ACCOUNTS_FIELDS = (
    ('customer__partner__company_name', 'Partner Company Name'),
    ('customer__company_name', 'Customer Company Name'),
    ('customer__id', 'Customer ID'),
    ('active', 'Active'),
    ('payer_account_id', 'Payer Account ID'),
    ('linked_account_id', 'Linked Account ID'),
    ('root_email', 'Root Email'),
    ('iam_username', 'IAM Username'),
    ('iam_url', 'IAM Url'),
    ('friendly_name', 'Friendly Name'),
    ('delivery_sequence', 'Delivery Sequence'),
    ('mrr', 'MRR'),
    ('workload', 'Workload'),
    ('estimate_url', 'Estimate Url'),
    ('reference_number', 'Reference Number')
)

AWS_SALES_ORDER_FIELDS = (
    ('billing_date', 'Billing Date'),
    ('payer_account_id', 'Payer Account ID'),
    ('partner_id', 'Partner ID'),
    ('partner_jba_code', 'Partner JBA Code'),
    ('partner_company_name', 'Partner Company Name'),
    ('customer_id', 'Customer ID'),
    ('customer_company_name', 'Customer Company Name'),
    ('invoice_generated', 'Invoice Generated'),
    ('linked_account_id', 'Linked Account ID'),
    ('order_number', 'Web Order Number'),
    ('product_jba_code', 'Product JBA Code'),
    ('product_name', 'Product Name'),
    ('invoice_id', 'Invoice ID'),
    ('unblended_cost__sum', 'Unblended Cost (USD)'),
    ('unblended_cost__sum_inr', 'Unblended Cost (INR)'),
    ('blended_cost__sum', 'Blended Cost (USD)'),
    ('discount', 'Discount'),
    ('bonus_discount', 'Credits'),
    ('cost', 'Cost (INR)'),
    ('currency', 'Currency')
)

PENDING_REQUESTS_FIELDS = (
    ('vendor_name', 'Vendor'),
    ('partner__company_name', 'Parnter Company Name'),
    ('customer__company_name', 'Customer Company Name'),
    ('discount', 'Discount(%)'),
    ('account_status', 'Status'),
    ('reference_number', 'Reference Number'),
    ('created_at', 'Created At')
)

AWS_ORDERS_REPORT = (
    ('order_number', 'Order Number'),
    ('order_status', 'Order Status'),
    ('partner', 'Partner'),
    ('partner_jbacode', 'Partner JBA Code'),
    ('customer', 'Customer'),
    ('product_name', 'Product Name'),
    ('quantity', 'Quantity'),
    ('discount', 'Discount'),
    ('cost', 'Cost'),
    ('total_cost', 'Total Order Cost'),
    ('reference_number', 'Reference Number'),
    ('payer_account_id', 'Payer Account ID'),
    ('account_id', 'Linked Account ID'),
    ('iam_url', 'IAM Url'),
    ('workload', 'Workload'),
    ('root_email', 'Root Email'),
    ('mrr', 'MRR'),
    ('delivery_sequence', 'Delivery Sequence'),
    ('estimate_url', 'Estimate URL')
)

TRANSACTING_PARTNER_REPORT = (
    ('state', 'State'),
    ('state__count', 'No of Partners'),

)

CUSTOMER_SEGMENTATION_REPORT =(
    ('customer_vertical' ,'Customer vertical'),
    ('customer_vertical__count' ,'No of Customers')
)
