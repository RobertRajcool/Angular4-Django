import json

from rest_framework import viewsets
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from rest_framework.views import Response
from rest_framework import permissions
from rest_framework.decorators import list_route, detail_route
from customers.models import Customers, CustomerContacts, CloudAccounts, MicrosoftDomains, PendingRequests
from partner.models import PartnerUserDetails, ContactDetails, Partner
from customers.serializers import CustomersSerializer, CustomerContactsSerializer, CloudAccountsSerializer, \
    PendingRequestsSerializer
from django.db.models import Q
from customers.microsoft_api import MicrosoftApi
from rest_framework import status
from cloudapp.defaults import AppDefaults
from cloudapp.generics.hashers import AESCipher
from users.get_users import GetUsers
from customers.common_functions import CommonFunctions
from common.signals import send_mail_notifications
from common.custom_exceptions import RedValidationErr
from background_scripts.jba.jba_webservice import JBAWebService
from common.reports.ReportList import ReportList
from django_mysql.models.functions import JSONExtract
from cloudapp.generics.query_manager import JSON_CONTAINS_QUERY, CONTAINS_QUERY
from django.conf import settings
from dateutil.tz import tzutc
import datetime
import calendar


class CustomersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomersSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.profile.user_type == 'R':
            return Customers.objects.all()
        elif user.profile.user_type == 'P':
            partner = user.partner.first().partner
            return Customers.objects.filter(partner=partner)
        else:
            return Customers.objects.none()

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        order_by = query_params.pop('order_by', None)
        company_name = query_params.pop('company_name', None)
        search_text = query_params.pop('searchText', None)
        query_set = self.get_queryset()
        query_set = query_set.filter(deleted=False)
        partner_id = None
        if not request.user.is_superuser:
            if request.user.profile.user_type == 'P':
                partner_id = request.user.partner.first().partner.id
        if search_text is not None:
            query_set = query_set.filter(
                Q(company_name__icontains=search_text) |
                Q(address__icontains=search_text) |
                Q(city__icontains=search_text) |
                Q(state__icontains=search_text))
        if partner_id is not None:
            query_set = query_set.filter(partner_id=partner_id)
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        return Response({'records': CustomersSerializer(query_set, context={'request': request}, many=True).data,
                         'totalRecords': total_records})

    def saveContactDetails(self, data, customerId):
        customer_contact_obj = CustomerContacts()
        customer_contact_obj.name = data['name']
        customer_contact_obj.position = data['position']
        customer_contact_obj.email = data['email']
        customer_contact_obj.mobile = data['mobile']
        customer_contact_obj.customer_id = customerId
        customer_contact_obj.save()
        return True

    def create(self, request, *args, **kwargs):
        data = request.data
        tenant_id = None
        is_valid_domain = None
        if 'logo' in request.FILES:
            logo = request.FILES['logo']
            customer_data = json.loads(data['data'])
        else:
            logo = None
            customer_data = json.loads(data['data'])

        # initial_partner_obj = InitialPartner.objects.filter(id=1)

        customer_obj = Customers()
        if logo != None:
            customer_obj.logo = logo

        if not request.user.is_superuser:
            if request.user.profile.user_type == 'P':
                customer_data['partner_id'] = request.user.partner.first().partner.id

        if 'cloud_account' in customer_data.keys():
            cloud_account = customer_data['cloud_account']
            if cloud_account['type'] == 'MS':
                domain = cloud_account['details']['domain_name']
                if domain and domain != '':
                    ms_api = MicrosoftApi()
                    domain_exist = ms_api.check_domain_exists(domain)
                    if not domain_exist:
                        return Response('Invalid_domain')
                    else:
                        customer_info = ms_api.get_customer_from_domain(domain)
                        if 'companyProfile' in customer_info:
                            tenant_id = customer_info['companyProfile']['tenantId']
                            is_valid_domain = True

        customer_obj.company_name = customer_data['company_name']
        customer_obj.address = customer_data['address']
        customer_obj.city = customer_data['city']
        customer_obj.state = customer_data['state']
        customer_obj.Pincode = customer_data['postcode']
        customer_obj.country = customer_data['country']
        customer_obj.pan_number = customer_data['pan_number']
        customer_obj.customer_vertical = customer_data['customer_vertical'][0]['id']
        customer_obj.delivery_sequence = customer_data['delivery_sequence']
        customer_obj.segment = customer_data['segment'][0]['id']
        if 'partner_id' in customer_data:
            partnerId = customer_data['partner_id']
            customer_obj.partner_id = partnerId
        customer_obj.save()

        try:
            # Inserting primary contact details of Customer
            self.saveContactDetails(customer_data['primary_contact'], customer_obj.id)
        except Exception:
            return Response(Exception)

        try:
            # Inserting secondary contact details of Customer
            self.saveContactDetails(customer_data['secondary_contact'], customer_obj.id)
        except Exception:
            return Response(Exception)

        """ Validating and Storing customer's cloud account requirements """
        if 'cloud_account' in customer_data.keys():
            try:
                cloud_account_data = customer_data['cloud_account']
                if tenant_id is not None:
                    cloud_account_data['details']['tenant_id'] = tenant_id
                    cloud_account_data['details']['active'] = is_valid_domain
                    if is_valid_domain:
                        cloud_account_data['active'] = True
                cloud_account_data['customer'] = customer_obj.id
                cloud_account_serializer = CloudAccountsSerializer(data=cloud_account_data,
                                                                   context={'request': request})
                cloud_account_serializer.is_valid(raise_exception=True)
                cloud_account_serializer.save()
            except Exception:
                customer_obj.delete()
                return Response(Exception)

            if cloud_account['type'] == 'MS':
                domain = cloud_account_data['details']['domain_name']
                if tenant_id is None and domain != '':
                    data['customer'] = customer_obj.id
                    CloudAccountsViewSet.store_ms_domain(data, domain, cloud_account_serializer.data['id'])

        return Response(customer_obj.id)

    def partial_update(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        deleted = query_params.pop('mode', None)
        if deleted is not None:
            primary_id = int(kwargs['pk'])
            customer_object = Customers.objects.get(id=primary_id)
            customer_object.deleted = 1
            customer_object.save()
            return Response('deleted')
        else:
            return Response('something went wrong deleted')

    def retrieve(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        fetch_cloudaccounts = query_params.pop('fetch_cloudaccounts', False)

        instance = self.get_object()
        data = self.serializer_class(instance, context={'request': request}).data

        """ Fetching customer contacts """
        contacts_queryset = CustomerContacts.objects.filter(customer=instance)
        contacts = CustomerContactsSerializer(contacts_queryset, context={'request': request}, many=True).data
        data['contacts'] = contacts

        """ Fetching cloud account details """
        query_params.pop('decrypt_passwords', None)
        query_params.pop('form_data', None)
        return Response(data)

    @list_route(methods=['post'], url_path='edit')
    def getcustomer_details(self, request, *args, **kwargs):

        customer_id = request.data['id']
        queryset = Customers.objects.filter(id=customer_id)
        customerQueryResult = CustomerContacts.objects.filter(customer_id=customer_id)
        if customerQueryResult.count() == 1:
            customer_object = CustomerContacts()
            customer_object.customer = Customers.objects.filter(id=customer_id).first()
            customer_object.save()
            customerQueryResult = CustomerContacts.objects.filter(customer_id=customer_id)
        return Response(
            {'customerdetails': list(queryset.values()), 'customercontacts': list(customerQueryResult.values())})

    @list_route(methods=['post'], url_path='get-partner-deliverysequence')
    def get_delivery_sequence(self, request, *args, **kwargs):
        customer_id = request.data['id']
        if not request.user.is_superuser:
            if request.user.profile.user_type == 'P':
                partnerid = request.user.partner.first().partner.id
                partners_jba_code = Partner.objects.filter(id=partnerid).values('jba_code')
                jba_code = partners_jba_code[0]['jba_code']
                delivery_sequences, st_code = JBAWebService().fetch_partner_delivery_sequence(
                    partner_jba_code=jba_code.upper())
                if len(
                        delivery_sequences) != 0 and delivery_sequences != 'Failed to fetch delivery sequence from JBA : Invalid ipaddress type':

                    return Response(delivery_sequences)
                else:
                    delivery_sequences = []
                    return Response(delivery_sequences)
            else:
                partner_id = Customers.objects.filter(id=customer_id).values('partner_id')
                partner = int(partner_id[0]['partner_id'])
                partners_jba_code = Partner.objects.filter(id=partner).values('jba_code')
                delivery_sequences, st_code = JBAWebService().fetch_partner_delivery_sequence(
                    partner_jba_code=partners_jba_code[0]['jba_code'])
                if len(
                        delivery_sequences) != 0 and delivery_sequences != 'Failed to fetch delivery sequence from JBA : Invalid ipaddress type':

                    return Response(delivery_sequences)
                else:
                    delivery_sequences = []
                    return Response(delivery_sequences)

        else:
            partner_id = Customers.objects.filter(id=customer_id).values('partner_id')
            partner = int(partner_id[0]['partner_id'])
            partners_jba_code = Partner.objects.filter(id=partner).values('jba_code')
            delivery_sequences, st_code = JBAWebService().fetch_partner_delivery_sequence(
                partner_jba_code=partners_jba_code[0]['jba_code'])
            if len(
                    delivery_sequences) != 0 and delivery_sequences != 'Failed to fetch delivery sequence from JBA : Invalid ipaddress type':

                return Response(delivery_sequences)
            else:
                delivery_sequences = []
                return Response(delivery_sequences)

    @list_route(methods=['post'], url_path='update/(?P<id>[^/]+)')
    def update_customer(self, request, id, *args, **kwargs):
        customer_data = request.data['formvalues']
        jsonOjbect = json.loads(customer_data)
        # updating customer details starts here
        customerobject = Customers.objects.get(id=jsonOjbect['customerId'])
        customerobject.company_name = jsonOjbect['company_name']
        customerobject.address = jsonOjbect['address']
        customerobject.Pincode = jsonOjbect['postcode']
        customerobject.city = jsonOjbect['city']
        customerobject.state = jsonOjbect['state']
        customerobject.pan_number = jsonOjbect['pan_number']
        customerobject.delivery_sequence = jsonOjbect['delivery']
        customerobject.customer_vertical = jsonOjbect['customer_vertical'][0]['id']
        customerobject.segment = jsonOjbect['segment'][0]['id']
        if 'imagefile' in request.FILES:
            imagefiledetails = request.FILES['imagefile']
            customerobject.logo = imagefiledetails
        customerobject.save()

        # updating primary contact details for customer starts here
        contactobject = CustomerContacts.objects.get(id=jsonOjbect['contactId'])
        contactobject.name = jsonOjbect['contact_name']
        contactobject.position = jsonOjbect['position']
        contactobject.email = jsonOjbect['email']
        contactobject.mobile = jsonOjbect['mobile']
        contactobject.save()
        # updating secondary contact details starts here
        optionalconatct = CustomerContacts.objects.get(id=jsonOjbect['optionalId'])
        optionalconatct.name = jsonOjbect['optional_contact_name']
        optionalconatct.position = jsonOjbect['optional_contact_position']
        optionalconatct.email = jsonOjbect['optional_contact_email']
        optionalconatct.mobile = jsonOjbect['optional_contact_mobile']
        optionalconatct.save()
        returnResult = {'status': True}
        return Response(returnResult)

    # checking company name already exist
    @list_route(methods=['post'], url_path='check_companyname')
    def check_company(self, request, *args, **kwargs):
        companyName = request.data['company_name'];
        customerId = request.data['id'];
        queryset = Customers.objects.filter(company_name=companyName).exclude(id=customerId).exists()
        return Response(queryset)

    # checking pancard number already exist
    @list_route(methods=['post'], url_path='check_pan_number')
    def check_panNumber(self, request, *args, **kwargs):
        panNumber = request.data['pan_number'];
        customerId = request.data['id'];
        queryset = Customers.objects.filter(pan_number=panNumber).exclude(id=customerId).exists()
        return Response(queryset)

    @list_route(methods=['get'], url_path='get_partner_customer/(?P<id>[^/]+)')
    def partner_customer(self, request, id):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        order_by = query_params.pop('order_by', None)
        company_name = query_params.pop('company_name', None)
        search_text = query_params.pop('searchText', None)
        query_set = self.get_queryset()
        query_set = query_set.filter(deleted=False)
        partner_id = id

        if search_text is not None:
            query_set = query_set.filter(
                Q(company_name__icontains=search_text) |
                Q(address__icontains=search_text) |
                Q(pan_number__icontains=search_text))
        if partner_id is not None:
            query_set = query_set.filter(partner_id=partner_id)
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        return Response({'records': CustomersSerializer(query_set, context={'request': request}, many=True).data,
                         'totalRecords': total_records})

    @list_route(methods=['post'], url_path="search")
    def search_customers(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        search_text = request.data['search_text']
        search_field = request.data['search_field']
        filters = dict()
        filters['deleted'] = False
        filters['%s__icontains' % search_field] = search_text
        filters.update(query_params)

        queryset = self.get_queryset().filter(**filters)
        data = CustomersSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)

    # Searching customers based on partner
    @list_route(methods=['post'], url_path="(?P<id>[^/]+)/search")
    def search_customers_by_partner(self, request, id, *args, **kwargs):
        user_id = id
        partner_id = PartnerUserDetails.objects.get(user=user_id).partner_id
        search_text = request.data['search_text']
        search_field = request.data['search_field']
        filters = dict()
        filters['deleted'] = False
        filters['%s__icontains' % search_field] = search_text
        filters['partner'] = partner_id

        queryset = self.get_queryset().filter(**filters)[:10]
        data = CustomersSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)


class CustomerContactsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = CustomerContacts.objects.all()
    serializer_class = CustomerContactsSerializer

    def get_queryset(self):
        query_set = CustomerContacts.objects.all()
        return query_set

    def create(self, request, *args, **kwargs):
        customer_contact_data = request.data

        customer_contact_obj = CustomerContacts()
        customer_contact_obj.name = customer_contact_data['name']
        customer_contact_obj.position = customer_contact_data['position']
        customer_contact_obj.email = customer_contact_data['email']
        customer_contact_obj.mobile = customer_contact_data['mobile']
        customer_contact_obj.customer_id = 2
        customer_contact_obj.save()
        return Response(customer_contact_obj.id)


@method_decorator(permission_required('customers.list_cloudaccounts', raise_exception=True), name='list')
@method_decorator(permission_required('customers.view_cloudaccounts', raise_exception=True), name='retrieve')
@method_decorator(permission_required('customers.add_cloudaccounts', raise_exception=True), name='create')
@method_decorator(permission_required('customers.change_cloudaccounts', raise_exception=True), name='update')
@method_decorator(permission_required('customers.change_cloudaccounts', raise_exception=True), name='partial_update')
@method_decorator(permission_required('customers.delete_cloudaccounts', raise_exception=True), name='destroy')
class CloudAccountsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CloudAccountsSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.profile.user_type == 'R':
            return CloudAccounts.objects.all()
        elif user.profile.user_type == 'P':
            partner = user.partner.first().partner
            return CloudAccounts.objects.filter(customer__partner=partner)
        else:
            return []

    def create(self, request, *args, **kwargs):
        domain = None
        data = request.data
        send_email = False

        # Get tenant id for microsoft customers
        if data['type'] == 'MS':
            domain = data['details']['domain_name']
            standard_discount = 0 if 'standard_discount' not in data['details'] or \
                                     data['details']['standard_discount'] == '' else \
                float(data['details']['standard_discount'])
            # Possible statuses Approved, Rejected, Waiting
            discount_status = 'Approved' if standard_discount > 0 and standard_discount <= 5 else 'Waiting'
            data['details']['discount_status'] = discount_status
            if domain and domain != '':
                ms_api = MicrosoftApi()
                customer_info = ms_api.get_customer_from_domain(domain)
                if 'companyProfile' in customer_info:
                    tenant_id = customer_info['companyProfile']['tenantId']
                    data['details']['tenant_id'] = tenant_id
                    data['details']['active'] = True
                    data['active'] = True
                else:
                    send_email = True

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Send relationship request
        if send_email:
            sent = True
            # As this logic is covered in order approval steps
            # self.store_ms_domain(data, domain, serializer.data['id'])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        already_active = instance.active
        account_is_new = True
        details_field = instance.details

        data = request.data
        domain = ''
        send_email = False
        acc_type = data.get('type', instance.type)
        if acc_type == 'MS':
            domain = data['details']['domain_name']
            standard_discount = 0 if 'standard_discount' not in data['details'] or \
                                     data['details']['standard_discount'] == '' else \
                float(data['details']['standard_discount'])
            # Possible statuses Approved, Rejected, Waiting
            discount_status = 'Approved' if standard_discount > 0 and standard_discount <= 5 else 'Waiting'
            prev_status = ''
            if 'discount_status' in details_field:
                if details_field['discount_status'] != 'Approved':
                    data['details']['discount_status'] = discount_status
                    prev_status = details_field['discount_status']
            else:
                data['details']['discount_status'] = discount_status
            if domain and domain != '' and domain != details_field['domain_name']:
                ms_api = MicrosoftApi()
                customer_info = ms_api.get_customer_from_domain(domain)
                if 'companyProfile' in customer_info:
                    tenant_id = customer_info['companyProfile']['tenantId']
                    data['details']['tenant_id'] = tenant_id
                    data['details']['active'] = True
                    data['active'] = True
                    instance.active = True
                    instance.save()
                else:
                    send_email = True

            request._data = data

        elif acc_type == 'AWS':
            if instance.details.get('account_id', None) and instance.details['account_id'] != '':
                account_is_new = False
            if instance.customer.partner.pk != Customers.objects.get(pk=data['customer']).partner.pk:
                details_field['delivery_sequence'] = '000'

        # preserving JSON fields on Partial Update
        if request.method == 'PATCH':
            details_field.update(data['details'])
            request._data['details'] = details_field

        response = super(CloudAccountsViewSet, self).update(request=request, *args, **kwargs)

        # Send relationship request
        if send_email:
            sent = True
            # As this logic is covered in order approval steps
            # self.store_ms_domain(data, domain, instance.id)

        # Returning Error
        if response.status_text != 'OK':
            return response

        return response



    def send_mail_notification(self, data, email, partner_email):
        """
        Function to sent Email for relationship request
        :param data:
        :param email:
        :param partner_email:
        :return:
        """
        from common.mails.BaseMails import BaseMails
        BaseMails.send_mail(subject='REDINGTON: Relationship Request',
                            recipients=[email, partner_email],
                            template_name='ms_relationship_request.html',
                            template_data={'ms_link': data})
        return True

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        query_params.update(kwargs)

        return_as = query_params.pop('return_as', 'serialized_data')
        offset = int(query_params.pop('offset', '0'))
        end = int(query_params.pop('end', '10'))
        order_by = query_params.pop('order_by', 'id')

        # Pops unnecessary keywords
        query_params.pop("form_data", None)

        def order_by_field(alias):
            """ Order by field refiner """

            notations = {
                "customer_details.partner_name": "customer__partner__company_name",
                "customer_details.company_name": "customer__company_name"
            }
            reverse, alias = (True, alias[1:]) if alias[0] == '-' else (False, alias)
            return '-%s' % notations.get(alias, alias) if reverse else notations.get(alias, alias)

        query_set = self.get_queryset()

        """ Common Filtering """
        searchText = query_params.pop('searchText', None)
        if searchText is not None:

            """ Filtering on JSON fields """
            extra_query = {
                'where': [],
                'params': []
            }

            filter_fields = []
            account_type = query_params.get('type', None)
            if account_type == 'AWS':
                filter_fields = ['details__payer_account_id', 'details__account_id', 'details__reference_number']

            for field in filter_fields:
                q, v = JSON_CONTAINS_QUERY(field_name=field, lookup_value=searchText)
                extra_query['where'].append(q)
                extra_query['params'].append(v)

            extra_query['where'] = [' OR '.join(extra_query['where'])]
            json_filtered_query_set = query_set.extra(**extra_query)

            """ Filtering on regular fields & combining it with JSON filtered result """
            query_set = json_filtered_query_set | query_set.filter(
                Q(customer__partner__company_name__icontains=searchText) |
                Q(customer__company_name__icontains=searchText)
            )

        query_set = query_set.filter(**query_params).order_by(order_by_field(order_by))
        total_records = query_set.count()

        if end == -1:
            end = total_records

        query_set = query_set[offset:end]

        if return_as == 'queryset':
            return query_set

        serializer = CloudAccountsSerializer(query_set, context={'request': request}, many=True)

        return Response({'records': serializer.data, 'totalRecords': total_records})

    @list_route(methods=['post'], url_path='validate-domain')
    def validate_domain(self, request, **kwargs):
        form_data = request.data
        is_valid = False
        if form_data['type'] == 'MS':
            domain = form_data['details']['domain_name']
            ms_api = MicrosoftApi()
            is_valid = ms_api.check_domain_exists(domain)
        return Response(is_valid)

    @list_route(methods=['post'], url_path='update-cloud-account/(?P<cloud_id>[^/]+)')
    def update_cloud_account(self, request, cloud_id):
        form_data = request.data
        cloud_account = CloudAccounts.objects.get(id=cloud_id)
        details = cloud_account.details
        vendor_name = cloud_account.vendor.vendor_name
        if vendor_name == 'Microsoft':
            vendor_name = 'AZURE'

        new_request = True
        if cloud_account.type == 'MS':
            domain_name = details['domain_name']
            if domain_name and domain_name != '':
                new_request = False
        elif cloud_account.type == 'AWS':
            account_id = details['account_id']
            if account_id and account_id != '':
                new_request = False
        partner_id = cloud_account.customer.partner.id
        details['allow_order'] = form_data['allow']
        cloud_account.details = details
        cloud_account.save()
        # if form_data['allow'] == 'No':
        # For RED-400 we should store all the requests
        pending_request = PendingRequests.objects.filter(cloud_account=cloud_id)
        if not len(pending_request):
            reference_last_number = PendingRequests.objects.last()
            if not reference_last_number:
                reference = 'ORDN%05d' % 1
            else:
                reference = 'ORDN%05d' % (
                    reference_last_number.id + 1)
            pending_request = PendingRequests()
            pending_request.customer_id = cloud_account.customer_id
            pending_request.reference_number = reference
            pending_request.partner_id = partner_id
            pending_request.cloud_account_id = cloud_id
            pending_request.vendor_id = cloud_account.vendor_id
            pending_request.created_by_id = request.user.id
            pending_request.save()
            details['reference_number'] = reference
            cloud_account.details = details
            cloud_account.save()
        else:
            pending_request = pending_request[0]

        subject = 'New account request for %s' % vendor_name
        message = 'new account'
        if not new_request:
            subject = 'Account link request for %s' % vendor_name
            message = 'account linking'

        standard_discount_val = cloud_account.details[
            'standard_discount'] if 'standard_discount' in cloud_account.details else 0

        send_mail_notifications.send(sender=PendingRequests, trigger='AccountRequest',
                                     details={'user': request.user, 'pending_request': pending_request,
                                              'vendor': cloud_account.vendor, 'partner': cloud_account.customer.partner,
                                              'customer': cloud_account.customer, 'subject': subject,
                                              'message': message, 'discount': standard_discount_val})
        return Response('success')

    @list_route(methods=['get'], url_path="validate")
    def validate_cloud_account(self, request, *args, **kwargs):
        """ Function to check is cloud account is active """
        query_params = request.query_params.dict()
        query_params.update(kwargs)

        queryset = self.get_queryset()
        vendor_prefix = query_params.pop('vendor_prefix', None)
        account = queryset.filter(type=vendor_prefix,
                                  customer_id=query_params.get('customer_id', None)).first()
        if (vendor_prefix != 'AWS') or (account is not None and account.active):
            serializer = self.serializer_class(account, context={'request': request})
            return Response(serializer.data)
        else:
            return Response(False)

    @method_decorator(permission_required('customers.list_cloudaccounts', raise_exception=True),
                      name='export_cloud_accounts')
    @list_route(methods=['get'], url_path='export/(?P<export_type>[A-Za-z]+)')
    def export_cloud_accounts(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        query_params['offset'] = 0
        query_params['end'] = -1
        export_type = kwargs.pop('export_type', 'csv')
        kwargs.update(query_params)

        queryset = self.list(request=request, *args, **kwargs, return_as='queryset')

        account_type = query_params.get('type', 'ALL')

        screen_name = 'Cloud Accounts'
        data_list = list()

        if account_type == 'AWS':
            screen_name = 'AWS Linked Accounts'
            data_list = queryset.annotate(payer_account_id=JSONExtract('details', '$.payer_account_id'),
                                          linked_account_id=JSONExtract('details', '$.account_id'),
                                          root_email=JSONExtract('details', '$.root_email'),
                                          iam_username=JSONExtract('details', '$.iam_username'),
                                          iam_password=JSONExtract('details', '$.iam_password'),
                                          iam_url=JSONExtract('details', '$.iam_url'),
                                          friendly_name=JSONExtract('details', '$.friendly_name'),
                                          delivery_sequence=JSONExtract('details', '$.delivery_sequence'),
                                          mrr=JSONExtract('details', '$.mrr'),
                                          workload=JSONExtract('details', '$.workload'),
                                          estimate_url=JSONExtract('details', '$.estimate_url'),
                                          reference_number=JSONExtract('details', '$.reference_number')) \
                .values('customer__partner__company_name',
                        'customer__company_name',
                        'customer__id',
                        'active',
                        'payer_account_id',
                        'linked_account_id',
                        'root_email',
                        'iam_username',
                        'iam_password',
                        'iam_url',
                        'friendly_name',
                        'delivery_sequence',
                        'mrr',
                        'workload',
                        'estimate_url',
                        'reference_number')

        file_generator = ReportList()
        response = file_generator.export(data_list=data_list,
                                         screen_name=screen_name,
                                         export_type=export_type,
                                         report_name='customer_aws_accounts_list')
        return response

    @method_decorator(permission_required('customers.list_cloudaccounts', raise_exception=True),
                      name='decrypt_password')
    @detail_route(methods=['get'], url_path="get-password-raw")
    def decrypt_password(self, request, *args, **kwargs):
        """
        :param request:
        :param args: 'pk'
        :param kwargs:
        :param query_params:
            {
                'password_field' : 'Field name of password stored '
            }
        :return:
            {
                'password_field': 'Raw Password'
            }
        """
        instance = self.get_object()
        query_params = request.query_params.dict()
        password_field = query_params.get('field_name', None)

        if password_field is not None and password_field in instance.details:
            hashed = instance.details[password_field]
            cipher = AESCipher()
            raw = cipher.decrypt(hashed.encode())
            return Response({password_field: raw})

        else:
            raise RedValidationErr('Invalid password field')

    @list_route(methods=['get'], url_path="search")
    def search_cloud_accounts(self, request, *args, **kwargs):
        query_params = request.query_params.dict()

        data_fields = ['id',
                       'customer__id',
                       'customer__company_name'
                       ]
        filters = dict()
        filters['active'] = True

        if 'vendor_short_name' in query_params:
            filters['type'] = query_params.pop('vendor_short_name')

        filters.update(query_params)

        queryset = self.get_queryset().filter(**filters).order_by('customer__company_name')

        if filters.get('type', None) == 'AWS':
            queryset = queryset \
                .annotate(linked_account_id=JSONExtract('details', '$.account_id'))

            data_fields.append('linked_account_id')

        data = queryset.values(*data_fields)
        data = list(data)

        return Response(data=data, status=status.HTTP_200_OK)


class PendingRequestViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PendingRequestsSerializer

    def get_queryset(self):
        queryset = PendingRequests.objects.all().filter(active=False)
        return queryset

    def list(self, request, *args, **kwargs):
        t_zone = tzutc()
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))

        if 'end' in kwargs:
            query_params['end'] = kwargs['end']

        if query_params.get('end', 'infinite') == 'infinite':
            end = -1
            del query_params['end']
        else:
            end = int(query_params.pop('end', 5))

        order_by = query_params.pop('order_by', '-created_at')
        searchText = query_params.pop('searchText', None)
        year = int(query_params.pop('year')) if query_params.get('year', 'all') != 'all' else 'all'
        month = int(query_params.pop('month')) if query_params.get('month', 'all') != 'all' else 'all'

        order_by_maps = {
            'customer_details.company_name': 'customer__company_name',
            '-customer_details.company_name': '-customer__company_name',
            'vendor_details.vendor_name': 'vendor__vendor_name',
            '-vendor_details.vendor_name': '-vendor__vendor_name',
            'customer_details.partner_name': 'partner__company_name',
            '-customer_details.partner_name': 'partner__company_name'
        }

        common_search_fields = ['customer__company_name', 'vendor__vendor_name', 'reference_number']

        order_by = order_by_maps.get(order_by, order_by)

        query_set = self.get_queryset()

        user = self.request.user
        if user.profile.user_type != 'P':
            user_object = GetUsers()
            vendors = user_object.get_vendors_associated_to_user(user.id)
            if len(vendors):
                query_set = query_set.filter(vendor_id__in=vendors)

            common_search_fields.append('partner__company_name')

        if user.profile.user_type == 'P':
            partnerid = self.request.user.partner.first().partner.id
            query_set = query_set.filter(Q(partner_id=partnerid))

        """ Year & Month filtering """
        if year != 'all':
            start_date = datetime.datetime(year=year,
                                           month=month if month != 'all' else 1,
                                           day=1,
                                           tzinfo=t_zone)
            end_month = month if month != 'all' else 12
            end_date = datetime.datetime(year=start_date.year,
                                         month=end_month,
                                         day=calendar.monthrange(start_date.year, end_month)[1],
                                         tzinfo=t_zone) + datetime.timedelta(days=1)

            query_set = query_set.filter(created_at__gte=start_date, created_at__lt=end_date)

        if searchText is not None:
            common_filter_q = None
            for field in common_search_fields:
                q = Q(**{'%s__icontains' % field: searchText})
                common_filter_q = common_filter_q | q if common_filter_q is not None else q

            query_set = query_set.filter(common_filter_q).distinct()

        """ Sorting queryset """
        query_set = query_set.order_by(order_by)

        total_records = query_set.count()

        if end < 0:
            end = total_records

        query_set = query_set[offset:end]
        records = PendingRequestsSerializer(query_set, context={'request': request}, many=True).data
        for record in records:
            record['links_to_show'] = ['View']
            record['partner_details'] = record['partner_details']
            record['partner_details']['email'] = record['partner_details']['contacts'][0]['email']
            record['partner_details']['mobile'] = record['partner_details']['contacts'][0]['mobile']
            record['account_status'] = ''
            record['discount'] = ''
            details = record['cloud_account_details']['details']
            vendor_type = record['cloud_account_details']['type']
            if 'discount_status' in details and vendor_type == 'MS' or vendor_type == 'SoftLayer' and 'discount_status' in details:
                record['account_status'] = details['discount_status']
                record['discount'] = details['standard_discount']
                if details['discount_status'] == 'Waiting':
                    record['links_to_show'] = ['View', 'Approve', 'Reject']
            else:
                record['discount'] = '-'
                if record['active']:
                    record['account_status'] = 'Active'
                else:
                    record['account_status'] = 'InActive'

        return Response({'records': records, 'totalRecords': total_records})

    @method_decorator(permission_required('customers.list_pendingrequests', raise_exception=True), name='')
    @list_route(methods=['get'], url_path='export/(?P<export_type>[A-Za-z]+)')
    def export_pending_requests(self, request, *args, **kwargs):
        query_params = request.query_params.dict()

        file_generator = ReportList()

        data_list = self.list(request=request, args=args, end='infinite', **kwargs).data['records']

        for record in data_list:
            record['vendor_name'] = record['vendor_details']['vendor_name']
            record['partner__company_name'] = record['partner_details']['company_name']
            record['customer__company_name'] = record['customer_details']['company_name']

        file_content_response = file_generator.export(screen_name='Pending_requests',
                                                      data_list=list(data_list),
                                                      export_type=kwargs.get('export_type', 'csv'),
                                                      report_name='pending_requests_list'
                                                      )
        return file_content_response


class MsCustomerViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CloudAccountsSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.profile.user_type == 'R':
            return CloudAccounts.objects.all().filter(type='MS')
        elif user.profile.user_type == 'P':
            partner = user.partner.first().partner
            return CloudAccounts.objects.filter(type='MS', customer_id__partner=partner)
        else:
            return []

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        order_by = query_params.pop('order_by', None)
        company_name = query_params.pop('company_name', None)
        search_text = query_params.pop('searchText', None)
        query_set = self.get_queryset()

        if search_text is not None:
            query_set = query_set.filter(
                Q(customer_id__company_name__icontains=search_text) |
                Q(customer_id__partner__company_name__icontains=search_text))

        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        return Response({'records': CloudAccountsSerializer(query_set, context={'request': request}, many=True).data,
                         'totalRecords': total_records})
