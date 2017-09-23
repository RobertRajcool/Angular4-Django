/**
 * Created by robert on 10/3/17.
 */

export class RedConstants {
    public static  EXCELREPORT_STATUS = 2001;
    public static  PDFREPORT_STATUS= 2002;
    public static NORMAL_PRODUCTS = 1
    public static AMAZON_VENDOR = "AWS";
    public static IBM_PRODUCTS = 2
    public static IBM_VENDOR='SoftLayer'
    public static MS_VENDOR = 'AZURE';
    public static CLOUD_VENDORS=['AZURE','AWS','SoftLayer']
    public static CREATE_QUOTE_STATUS=10001
    public static CREATE_ORDER_STATUS=10002
    public static FEEDBACK_OPTION = [
        'Marketplace',
        'Orders',
        'Reports',
        'Invoices',
        'Redington Cloud solutions',
        'Users',
        'Products',
        'AWS Agreement Signup',
        'Accounting & Billing Questions',
        'Sales Enquiries',
        'Portal Information , Issues, & Questions',
        'Product Information',
        'Technical Support',
        'Others',
    ];
    public static AZURE_BILLIING_CYCLE_DATE = 22;
    public static FILE_CONTENT_TYPES = {
        'csv': ['text/csv', 'csv'],
        'xls': ['application/vnd.ms-excel', 'xls'],
        'xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx']
    }
    public static IsvUserTypes: Array<string> = ['I','RI'];

    public static ISV_FEEDBACK_OPTION=[
      'ISV Product Registration',
      'Trial Account Details',
      'Services'
    ]
    public static Trial_Current_email_solution=[
      'Office365',
      'Google Apps(Now G Suite)',
      'Hosted Exchange',
      'MS Exchange On-premise',
      'Mithi Skyconnect',
      'Connect Xf(On premise)',
      'Zimbra',

    ]

}
