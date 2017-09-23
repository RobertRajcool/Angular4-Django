import json, datetime
from rest_framework import viewsets
from customers.models import Customers, CustomerContacts
from rest_framework.views import Response
from rest_framework import permissions
from rest_framework.decorators import list_route
from django.utils.crypto import get_random_string
from partner.models import Partner, DocumentDetails, ContactDetails, InitialPartner, \
    InitialContactDetails, InitialDocumentDetails, PartnerUserDetails, PartnerRejections, AwsCredits, PartnerRating
from partner.serializers import PartnerSerializer, InitialPartnerSerializer, AwsCreditsSerializer, PartnerRatingSerializer
from common.signals import send_mail_notifications
from users.models import RedUser, UserProfile
from django.contrib.auth.models import Group
from cloudapp.defaults import AppDefaults
from django.db.models import Q
from django.conf import settings
from customers.microsoft_api import MicrosoftApi
import requests
from django.utils import timezone
from customers.models import CloudAccounts
from customers.serializers import CloudAccountsSerializer
from background_scripts.jba.jba_apis import PARTNER_EMAIL_UPDATE
from django.core.mail import EmailMessage
from redington_uber.settings import DEVELOPER_EMAILS
from common.models import RedTokens


class PartnerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', '-activated_at')
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(
                Q(company_name__icontains=searchText) |
                Q(city__icontains=searchText) |
                Q(jba_code__icontains=searchText) |
                Q(contacts__email__icontains=searchText)
            ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)

        """Sorting"""
        query_set = query_set.filter(customer=0)
        query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data

        for index, record in enumerate(data):
            if not record['contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['contacts'][0]['name']
                data[index]['mobile'] = record['contacts'][0]['mobile']
                data[index]['email'] = record['contacts'][0]['email']
        return Response({'records': data, 'totalRecords': total_records})

    @list_route(methods=['get'], url_path='active-customers')
    def active_customers(self, request):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', '-activated_at')
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(
                Q(company_name__icontains=searchText) |
                Q(city__icontains=searchText) |
                Q(jba_code__icontains=searchText) |
                Q(contacts__email__icontains=searchText)
            ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)

        """Sorting"""
        query_set = query_set.filter(customer=1)
        query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data

        for index, record in enumerate(data):
            if not record['contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['contacts'][0]['name']
                data[index]['mobile'] = record['contacts'][0]['mobile']
                data[index]['email'] = record['contacts'][0]['email']
        return Response({'records': data, 'totalRecords': total_records})

    @list_route(methods=['get'], url_path='unlinked-customers')
    def unlinked_customers(self, request):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', '-activated_at')
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(
                Q(company_name__icontains=searchText) |
                Q(city__icontains=searchText) |
                Q(jba_code__icontains=searchText) |
                Q(contacts__email__icontains=searchText)
            ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)

        """Sorting"""
        query_set = query_set.filter(customer=1)
        query_set = query_set.order_by(order_by)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data

        for index, record in enumerate(data):
            if not record['contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['contacts'][0]['name']
                data[index]['mobile'] = record['contacts'][0]['mobile']
                data[index]['email'] = record['contacts'][0]['email']

            record['links_to_show'] = ['View', 'Delink'] if record['orc_link_code'] else ['Add']

        return Response({'records': data, 'totalRecords': total_records})

    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/customer-linking')
    def customer_linking(self, request, id):
        data = request.data['partner']
        if len(data) > 0:
            Partner.objects.filter(id=id).update(partner=data[0]['id'])
            return Response(True)
        else:
            return Response(False)

    @list_route(methods=['get'], url_path='(?P<id>[^/]+)/customer-delinking')
    def customer_delinking(self, request, id):
        Partner.objects.filter(id=id).update(partner=None)

        return Response(True)

    # Partner activation and creating login credentials for partner
    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/activate')
    def activate_partner(self, request, id):
        initial_partner_detail = request.data

        initial_partner_obj = InitialPartner.objects.filter(id=id)
        initial_partner_obj.update(status=1, credits=int(initial_partner_detail['credits']),
                                   jba_code=initial_partner_detail['jba_code'],
                                   preferred_user_name=initial_partner_detail['preferred_user_name'])

        initial_partner_values = InitialPartner.objects.filter(id=id)
        serializer = InitialPartnerSerializer(initial_partner_values, many=True, context={'request': request})
        current_user = request.user

        try:
            activated_partner_id = self.store_activated_partner_details(serializer.data[0])
        except Exception:
            return Exception

        try:
            password = get_random_string(length=7)
            initial_contact = InitialContactDetails.objects.get(partner=id, type='P')
            email = initial_contact.email
            name = initial_contact.name
            RedUser.objects.create_user(username=initial_partner_detail['preferred_user_name'], email=email,
                                        password=password, last_name=name)
            created_user_id = RedUser.objects.get(username=initial_partner_detail['preferred_user_name']).pk
        except Exception:
            return Exception

        try:
            self.store_partner_user_details(activated_partner_id, created_user_id)
        except Exception:
            return Exception

        try:
            user_id = RedUser.objects.get(username=initial_partner_detail['preferred_user_name']).pk
            self.create_partner_profile(user_id, initial_partner_obj.first(), current_user)
        except Exception:
            return Exception

        if initial_partner_values.first().customer:
            self.create_customer(Partner.objects.filter(pk=activated_partner_id).first())

        try:
            details = {
                'partner_detail': serializer.data[0],
                'password': password
            }
            send_mail_notifications.send(sender=InitialPartner, trigger='PartnerActivation', details=details)
        except Exception:
            return Exception

        try:
            self.remove_partner(id)
        except Exception:
            return Exception

        return Response(True)

    def create_customer(self, partner):
        customer = Customers()
        customer.partner_id = partner.id
        customer.company_name = partner.company_name
        customer.address = partner.address_1 if partner.address_1 else '' + '' + partner.address_2 if partner.address_2\
            else ''
        customer.city = partner.city
        customer.state = partner.state
        customer.Pincode = partner.pin_code
        customer.country = partner.state
        customer.pan_number = ''
        customer.deleted = False
        customer.customer_vertical = None
        customer.delivery_sequence = '000'
        customer.save()

        ''' Creating customer contacts1 '''
        self.create_customer_contacts(customer)

        ''' Creating customer contacts2 '''
        self.create_customer_contacts(customer)

    def create_customer_contacts(self, customer):
        cntct = ContactDetails.objects.filter(partner_id=customer.partner_id, type='P').first()
        contacts = CustomerContacts()
        contacts.customer_id = customer.id
        contacts.name = cntct.name
        contacts.position = ''
        contacts.email = cntct.email
        contacts.mobile = cntct.mobile
        contacts.save()

    # Partner rejection and sending notification to partner
    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/reject')
    def reject_partner(self, request, id):
        rejection_detail = request.data

        initial_partner_values = InitialPartner.objects.filter(id=id)
        serializer = InitialPartnerSerializer(initial_partner_values, many=True, context={'request': request})

        url_key = InitialPartner.objects.get(id=id).key

        domain = settings.DOMAIN_NAME
        if 'HTTP_ORIGIN' in request.META:
            domain = request.META['HTTP_ORIGIN']

        url_str = domain+'/'+url_key+'/registration/'
        current_user = request.user

        partner_rejection_obj = PartnerRejections()
        partner_rejection_obj.partner = InitialPartner.objects.get(id=id)
        partner_rejection_obj.rejection_reason = rejection_detail['rejection_reason']
        partner_rejection_obj.rejected_by = RedUser.objects.get(id=current_user.id)
        partner_rejection_obj.save()

        initial_partner_obj = InitialPartner.objects.filter(id=id)
        initial_partner_obj.update(registration_status=4)

        details = {
            'partner_detail': serializer.data[0],
            'rejection_reason': rejection_detail['rejection_reason'],
            'url': url_str
        }

        try:
            send_mail_notifications.send(sender=InitialPartner, trigger='PartnerRejection', details=details)
        except Exception:
            return Exception

        return Response(True)

    @list_route(methods=['post'], url_path='check-jbacode')
    def check_jbacode(self, request, *args, **kwargs):
        jba_code = request.data
        queryset = Partner.objects.filter(jba_code=jba_code)
        querysetlength = len(queryset)
        return Response(querysetlength)

    # Check dealer code (JBA code) exists
    @list_route(methods=['post'], url_path='(?P<code>[^/]+)/check_dealer_code')
    def check_dealer_code_exists(self, request, code):
        if Partner.objects.filter(jba_code=code).exists():
            return Response(False)
        else:
            return Response(True)

    # Check user name exists in database
    @list_route(methods=['post'], url_path='(?P<name>[^/]+)/check')
    def check_user_name(self, request, name):
        if RedUser.objects.filter(username=name).exists():
            return Response(False)
        else:
            return Response(True)

    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/update')
    def update_partner(self, request, id):
        partner_details = request.data
        business_type = partner_details['business_type']
        focused_customer = partner_details['focused_customer']
        interested_workload = partner_details['interested_workload']
        partner_type = partner_details['partner_type']
        business_id = []
        customer_id = []
        workload_id = []
        partner_id = []

        contact = [{'id': partner_details['contact_id'],
                   'name': partner_details['name'],
                   'email': partner_details['email'],
                   'mobile': partner_details['mobile']}]

        for business in business_type:
            business_id.append(str(business['id']))

        business_id_str = ', '.join(business_id)

        for customer in focused_customer:
            customer_id.append(str(customer['id']))

        customer_id_str = ', '.join(customer_id)

        for workload in interested_workload:
            workload_id.append(str(workload['id']))

        workload_id_str = ', '.join(workload_id)

        for partner in partner_type:
            if partner['checked'] == True:
                partner_id.append(str(partner['id']))

        partner_id_str = ', '.join(partner_id)

        partnerObj = Partner.objects.filter(id=id)
        partnerObj.update(status=partner_details['status'],
                          company_name= partner_details['company_name'],
                          jba_code=partner_details['jba_code'],
                          credits=partner_details['credits'],
                          vendor_list=partner_details['vendor_list'],
                          address_1=partner_details['address_1'],
                          address_2=partner_details['address_2'],
                          address_3=partner_details['address_3'],
                          city=partner_details['city'],
                          state=partner_details['state'],
                          pin_code=partner_details['pin_code'],
                          partner_type=partner_id_str,
                          business_type=business_id_str,
                          focused_customer=customer_id_str,
                          interested_workload=workload_id_str,
                          gst_number=partner_details['gst_number'],
                          updated_at=datetime.datetime.now())
        try:
            self.update_partner_contact_details(contact, 'primary')
        except Exception:
            return Exception
        try:
            self.update_secondary_contact_details(partner_details['contactGroup'], 'secondary')
        except Exception:
            return Exception

        email_details = [{'email': partner_details['email']}]
        contact_details = partner_details['contactGroup']
        secondary_contacts = contact_details.values()

        for secondary_contact in secondary_contacts:
            contact_type = ContactDetails.objects.filter(id=secondary_contact['id']).first().type
            if contact_type != 'S':
                value = {'email': secondary_contact['email']}
                email_details.append(value)

        try:
            self.update_partner_contacts_to_jba(email_details, id)
        except Exception:
            return Exception

        partner_value = Partner.objects.filter(id=id)
        serializer = PartnerSerializer(partner_value, many=True, context={'request': request})

        return Response(serializer.data[0])

    @list_route(methods=['post'], url_path='search-partner')
    def search_partner(self, request, **kwargs):
        search_text = request.data['search_text']
        search_field = request.data['search_field']
        filters = dict()
        # filters['profile__user_type'] = 'P'
        filters['%s__icontains' % search_field] = search_text

        query_set = self.get_queryset()

        queryset = query_set.filter(**filters)
        data = PartnerSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)

    @list_route(methods=['post'], url_path='apn-search-partner')
    def apn_search_partner(self, request, **kwargs):
        search_text = request.data['search_text']
        search_field = request.data['search_field']
        filters = dict()
        # filters['profile__user_type'] = 'P'
        filters['%s__icontains' % search_field] = search_text

        query_set = self.get_queryset().exclude(apn_id__isnull=True).exclude(apn_id__exact='')

        queryset = query_set.filter(**filters)
        data = PartnerSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)

    @list_route(methods=['get'], url_path='current_partner_details')
    def current_partner_details(self, request, **kwargs):
        partner_user = PartnerUserDetails.objects.get(user_id=request.user.id)
        partner_query_set = Partner.objects.filter(id=partner_user.partner_id)
        partner = list(partner_query_set.values())

        return Response(partner[0])

    @list_route(methods=['get'], url_path='apn_partner_details')
    def apn_partner_details(self, request):
        query_set = self.get_queryset().filter(apn_id_active=False)
        queryset = query_set.exclude(apn_id__isnull=True).exclude(apn_id__exact='')

        data = PartnerSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)

    @list_route(methods=['post'], url_path='update-mpn-id')
    def update_mpn_id(self, request, **kwargs):
        form_data = request.data
        mpn_id = form_data['mpn_id']
        ms_api = MicrosoftApi()
        is_valid = ms_api.validate_mpn_id(mpn_id)

        if is_valid:
            # partner_user = PartnerUserDetails.objects.get(user_id=request.user.id)
            partner_object = Partner.objects.get(id=form_data['partner_id'])
            partner_object.mpn_id = mpn_id
            partner_object.save()

        return Response(is_valid)

    @list_route(methods=['post'], url_path='update-apn-id')
    def update_apn_id(self, request, **kwargs):
        form_data = request.data
        apn_id = form_data['apn_id']

        partner_user = PartnerUserDetails.objects.get(user_id=request.user.id)
        partner_object = Partner.objects.get(id=partner_user.partner_id)
        partner_object.apn_id = apn_id
        partner_object.save()

        data = Partner.objects.get(id=partner_user.partner_id)

        send_mail_notifications.send(sender=Partner, trigger='ApnidUpdated', details={'user': request.user, 'partner_details': data})

        return Response(True)

    @list_route(methods=['post'], url_path='activate-apn-id')
    def activate_apn_account(self, request, *args, **kwargs):
        form_data = request.data
        apn_active = form_data['apn_active']
        apn_id = form_data['apn_id']
        partner_id = form_data['partner_id']

        partner_object = Partner.objects.filter(id=partner_id)
        partner_object.update(apn_id=apn_id, apn_id_active=apn_active)

        return Response(True)

    def update_secondary_contact_details(self, contactDetails, type):
        try:
            self.update_partner_contact_details(contactDetails.values(), type)
        except:
            return Exception

        return True

    def update_partner_contact_details(self, contacts, type):
        for contact in contacts:
            contact_id = contact['id']
            contact_obj = ContactDetails.objects.filter(id=contact_id)
            contact_obj.update(name=contact['name'], email=contact['email'], mobile=contact['mobile'])
            if type == 'primary':
                partner_id = ContactDetails.objects.filter(id=contact_id).first().partner_id
                user_id = PartnerUserDetails.objects.filter(partner_id=partner_id).first().user.id
                user_obj = RedUser.objects.filter(id=user_id)
                user_obj.update(email=contact['email'])

        return True

    def update_partner_contacts_to_jba(self, email_details, partner_id):

        jba_code = Partner.objects.get(id=partner_id).jba_code
        partner_name = Partner.objects.get(id=partner_id).company_name
        headers = {'Content-Type': 'application/json'}
        data = {'CustCode': str.strip(str.upper(jba_code)) , 'Email1': email_details[0]['email'], 'Email2': email_details[1]['email'], 'Email3': email_details[2]['email']}
        partner_details_out = requests.post(PARTNER_EMAIL_UPDATE, data=json.dumps(data), headers=headers)

        if partner_details_out.text != '"Y"':
            data = "JBA call failed while updating partner's contact for JBA Code: " + str.strip(str.upper(jba_code))
            msg = EmailMessage('Partner Contact failed to update partner ' + partner_name, data,
                               from_email='cloudsupport@redington.co.in',
                               to=DEVELOPER_EMAILS)
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)

        return True

    # Storing activated partner details in Partner model
    def store_activated_partner_details(self, partner_detail):
        partner_obj = Partner()
        partner_obj.customer = partner_detail['customer']
        partner_obj.company_name = partner_detail['company_name']
        partner_obj.status = partner_detail['status']
        partner_obj.existing_status = partner_detail['existing_status']
        partner_obj.gst_number = partner_detail['gst_number']
        partner_obj.jba_code = partner_detail['jba_code']
        partner_obj.credits = partner_detail['credits']
        partner_obj.address_1 = partner_detail['address_1']
        partner_obj.address_2 = partner_detail['address_2']
        partner_obj.address_3 = partner_detail['address_3']
        partner_obj.city = partner_detail['city']
        partner_obj.state = partner_detail['state']
        partner_obj.pin_code = partner_detail['pin_code']
        partner_obj.partner_type = partner_detail['partner_type']
        partner_obj.business_type = partner_detail['business_type']
        partner_obj.focused_customer = partner_detail['focused_customer']
        partner_obj.interested_workload = partner_detail['interested_workload']
        partner_obj.created_at = partner_detail['created_at']
        partner_obj.updated_at = partner_detail['updated_at']
        partner_obj.activated_at = datetime.datetime.now()
        partner_obj.save()

        try:
            self.store_activated_partner_contact_details(partner_obj.id, partner_detail['initial_contacts'])
        except Exception:
            return Exception

        try:
            self.store_activated_partner_document_details(partner_obj.id, partner_detail['initial_documents'])
        except Exception:
            return Exception

        return partner_obj.id

    # Storing activated partner contact details
    def store_activated_partner_contact_details(self, partner_id, contact_detail):
        for contacts in contact_detail:
            contact_obj = ContactDetails()
            contact_obj.partner = Partner.objects.get(id=partner_id)
            contact_obj.type = contacts['type']
            contact_obj.name = contacts['name']
            contact_obj.email = contacts['email']
            contact_obj.mobile = contacts['mobile']
            contact_obj.save()

        return True

    # Storing activated partner document details
    def store_activated_partner_document_details(self, partner_id, document_detail):
        #url = settings.LOCAL_HOST + settings.MEDIA_URL
        for documents in document_detail:
            intial_document_object = InitialDocumentDetails.objects.get(id=documents['id'])
            #data = documents['file_data'].replace(url, '')
            document_obj = DocumentDetails()
            document_obj.partner = Partner.objects.get(id=partner_id)
            document_obj.file_name = documents['file_name']
            document_obj.file_data = intial_document_object.file_data
            document_obj.type = documents['type']
            document_obj.save()

        return True

    # Creating partner user profile
    def create_partner_profile(self, user_id, partner_detail, current_user):
        user = RedUser.objects.get(id=user_id)
        role_id = 0
        permission_group_name = AppDefaults.get_predefined_roles()

        if partner_detail.customer:
            if Group.objects.filter(name=permission_group_name['Customer']).exists():
                user.groups = Group.objects.filter(name=permission_group_name['Customer'])
                role_id = Group.objects.get(name=permission_group_name['Customer']).id
        else:
            if Group.objects.filter(name=permission_group_name['Partner']).exists():
                user.groups = Group.objects.filter(name=permission_group_name['Partner'])
                role_id = Group.objects.get(name=permission_group_name['Partner']).id

        user_profile_obj = UserProfile()
        user_profile_obj.user = user
        user_profile_obj.user_type = 'P'
        user_profile_obj.created_by = RedUser.objects.get(id=current_user.id)
        user_profile_obj.role_id = role_id
        user_profile_obj.save()

        return True

    # Removing partner from InitialPartner model
    def remove_partner(self, partner_id):
        InitialContactDetails.objects.filter(partner=partner_id).delete()
        InitialDocumentDetails.objects.filter(partner=partner_id).delete()
        InitialPartner.objects.filter(id=partner_id).delete()

        return True

    # Storing partner user details in PartnerUserDetails model
    def store_partner_user_details(self, partner_id, user_id):
        partner_user_obj = PartnerUserDetails()
        partner_user_obj.partner = Partner.objects.get(id=partner_id)
        partner_user_obj.user = RedUser.objects.get(id=user_id)
        partner_user_obj.save()

        return True

    @list_route(methods=['get'], url_path='partner_list')
    def get_partner_list(self, request):
        i = datetime.datetime.now()
        year = i.year
        month = i.month
        last_month = month - (1)
        query_set = self.queryset
        user = self.request.user

        partnerlist_current_month = query_set.filter(activated_at__month=month, activated_at__year=year).count()

        partnerlist_last_month = query_set.filter(activated_at__month=last_month, activated_at__year=year).count()

        partnerlist_count = query_set.filter(activated_at__year=year).count()

        return Response(
            {'partnerlist_current_month_count': partnerlist_current_month,
             'partnerlist_last_month_count': partnerlist_last_month,
             'total_partnerlist_count': partnerlist_count,
             'current_year': year})

    @list_route(methods=['get'], url_path="get_credits/(?P<id>[^/]+)")
    def get_credit_values(self, request, id, *args, **kwargs):
        user_id = id
        partner_id = PartnerUserDetails.objects.get(user=user_id).partner_id
        jba_code = Partner.objects.get(id=partner_id).jba_code

        out = requests.get('http://edi.redingtonb2b.in/redcloudstaging/api/RedingtonCloudApi/GetPartner?CustomerCode='+ str.strip(str.upper(jba_code)))
        if out.status_code == 200:
            value = out.json()
            data = {
                'availableLimit': value[0]['AvalLmt'] if value else 0,
                'creditLimit': value[0]['CredLmt'] if value else 0,
                'creditDay': value[0]['CreditDay'] if value else 0,
                'customerCode': value[0]['CusCode'] if value else '',
                'customerFlag': value[0]['CusFlag'] if value else '',
                'customerName': value[0]['CusNam'] if value else '',
                'overDue': value[0]['OvrDueBal'] if value else 0,
                'totalOutstanding': value[0]['ToTOut'] if value else 0
            }
        else:
            data = {
                'availableLimit': 0,
                'creditLimit': 0,
                'creditDay': 0,
                'customerCode': '',
                'customerFlag': '',
                'customerName': '',
                'overDue': 0,
                'totalOutstanding': 0
            }

        return Response(data)

    @list_route(methods=['get'], url_path='download_active_partner_list')
    def download_active_partner_list(self, request):
        queryset = self.queryset
        data = self.serializer_class(queryset, context={'request': request}, many=True).data
        # arrange data as we need
        inital_view_set = InitialPartnerViewSet()
        for index, record in enumerate(data):
            data[index]['existing_status'] = 'Yes' if record['existing_status'] else 'No'
            data[index]['business_type'] = inital_view_set.get_formatted_partner_business_type(record['business_type'])
            data[index]['focused_customer'] = inital_view_set.get_formatted_customer_vertical(record['focused_customer'])
            data[index]['partner_type'] = inital_view_set.get_formatted_partner_type(record['partner_type'])
            data[index]['interested_workload'] = inital_view_set.get_formatted_partner_workload(record['interested_workload'])
            if not record['contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
                data[index]['email_1'] = ''
                data[index]['email_2'] = ''
                data[index]['email_3'] = ''
            else:
                data[index]['name'] = record['contacts'][0]['name']
                data[index]['mobile'] = record['contacts'][0]['mobile']
                data[index]['email'] = record['contacts'][0]['email']
                if len(record['contacts']) == 4:
                    data[index]['email_1'] = record['contacts'][1]['email']
                    data[index]['email_2'] = record['contacts'][2]['email']
                    data[index]['email_3'] = record['contacts'][3]['email']
                else:
                    data[index]['email_1'] = ''
                    data[index]['email_2'] = ''
                    data[index]['email_3'] = ''

        from common.reports.ReportFieldMapping import ReportFieldMapping
        report_field_mapping = ReportFieldMapping()
        fields_options = report_field_mapping.createReport('active_partner_list')
        from common.reports.ReportList import ReportList
        file_generator = ReportList()
        return file_generator.exportEXCELFile(data_list=data, screen_name='product list',
                                              field_mappings=fields_options)

    @list_route(methods=['get'], url_path='download_active_aws_partner_list')
    def download_active_aws_partner_list(self, request):
        queryset = self.queryset
        data = self.serializer_class(queryset.filter(apn_id_active=True), context={'request': request}, many=True).data
        # arrange data as we need
        inital_view_set = InitialPartnerViewSet()
        for index, record in enumerate(data):
            data[index]['existing_status'] = 'Yes' if record['existing_status'] else 'No'
            data[index]['business_type'] = inital_view_set.get_formatted_partner_business_type(record['business_type'])
            data[index]['focused_customer'] = inital_view_set.get_formatted_customer_vertical(
                record['focused_customer'])
            data[index]['partner_type'] = inital_view_set.get_formatted_partner_type(record['partner_type'])
            data[index]['interested_workload'] = inital_view_set.get_formatted_partner_workload(
                record['interested_workload'])
            if not record['contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['contacts'][0]['name']
                data[index]['mobile'] = record['contacts'][0]['mobile']
                data[index]['email'] = record['contacts'][0]['email']

        from common.reports.ReportFieldMapping import ReportFieldMapping
        report_field_mapping = ReportFieldMapping()
        fields_options = report_field_mapping.createReport('aws_active_partner_list')
        from common.reports.ReportList import ReportList
        file_generator = ReportList()
        return file_generator.exportEXCELFile(data_list=data, screen_name='active partner list',
                                              field_mappings=fields_options)

    @list_route(methods=['post'], url_path='store_partner_rating_and_feedback')
    def store_partner_rating_and_feedback(self, request):
        rating = PartnerRating()
        rating.rating = request.data['rating']
        rating.feedback = request.data['feedback']
        rating.partner = PartnerUserDetails.objects.filter(user=request.user).first().partner
        rating.save()

        return Response(True)

    @list_route(methods=['get'], url_path='is_partner_updated_feedback')
    def is_partner_updated_feedback(self, request):
        is_updated = PartnerRating.objects.filter(partner=PartnerUserDetails.objects.filter(user=request.user).
                                                  first().partner).exists()

        return Response(is_updated)

    @list_route(methods=['get'], url_path='get_ratings')
    def get_ratings(self, request):
        query_set = PartnerRating.objects.all()
        data = PartnerRatingSerializer(query_set, context={'request': request}, many=True).data

        return Response(data)

    @list_route(methods=['get'], url_path='get_ratings_count')
    def get_ratings_count(self, request):
        from django.db import connection

        cursor = connection.cursor()
        cursor.execute('''SELECT rating, COUNT(rating) FROM partner_partnerrating GROUP BY rating ORDER BY rating DESC''')

        return Response(cursor.fetchall())

    @list_route(methods=['post'], url_path='send-registration-link')
    def send_registration_link(self, request):
        from common.mails.BaseMails import BaseMails
        from common.views import RedTokenViewSet

        partner_obj = InitialPartner()
        partner_obj.key = get_random_string(length=16)
        partner_obj.status = 0
        partner_obj.registrations_status = 1
        partner_obj.existing_status = 0
        partner_obj.customer = 1
        partner_obj.company_name = request.data['customer']
        partner_obj.save()

        contact_obj = InitialContactDetails()
        contact_obj.partner = InitialPartner.objects.get(id=partner_obj.id)
        contact_obj.type = 'P'
        contact_obj.name = ''
        contact_obj.email = request.data['email']
        contact_obj.mobile = ''
        contact_obj.save()

        token = RedTokenViewSet()
        token = token.generate_token(2, partner_obj.id)

        domain = settings.DOMAIN_NAME
        if 'HTTP_ORIGIN' in request.META:
            domain = request.META['HTTP_ORIGIN']
        data = dict()
        data['customer'] = request.data['customer']
        data['link'] = domain+'/'+partner_obj.key+'/registration?tk='+token

        BaseMails.send_mail(subject='Customer registration link',
                            recipients=[request.data['email']],
                            template_name='customer_registration_link.html',
                            template_data=data, attachements=None, attachments_full_path=None)

        return Response(True)

    @list_route(methods=['get'], url_path='selected_partner')
    def selected_partner(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        partner_ids = query_params.pop("partner_ids", 'all')
        data = []
        if partner_ids != 'all':
            partner_ids = list(map(lambda x: int(x), partner_ids.split(',')))
            queryset = Partner.objects.filter(id__in=partner_ids)
            records = self.serializer_class(queryset, context={'request': request}, many=True).data

            for record in records:
                value = {'id':record['id'], 'text': record['company_name']}
                data.append(value)

        return Response(data)


class InitialPartnerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = InitialPartner.objects.filter(registration_status=3)
    serializer_class = InitialPartnerSerializer

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', None)
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(Q(company_name__icontains=searchText) |
                Q(city__icontains=searchText) |
                Q(initial_contacts__email__icontains=searchText)
            ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)

        query_set = query_set.filter(customer=0, registration_status=3)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data
        for index, record in enumerate(data):
            if not record['initial_contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['initial_contacts'][0]['name']
                data[index]['mobile'] = record['initial_contacts'][0]['mobile']
                data[index]['email'] = record['initial_contacts'][0]['email']
        return Response({'records': data, 'totalRecords': total_records})

    @list_route(methods=['get'], url_path='inactive-customers')
    def inactive_customers(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', None)
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(Q(company_name__icontains=searchText) |
                Q(city__icontains=searchText) |
                Q(initial_contacts__email__icontains=searchText)
            ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)

        query_set = query_set.filter(customer=1, registration_status=3)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data
        for index, record in enumerate(data):
            if not record['initial_contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['initial_contacts'][0]['name']
                data[index]['mobile'] = record['initial_contacts'][0]['mobile']
                data[index]['email'] = record['initial_contacts'][0]['email']
        return Response({'records': data, 'totalRecords': total_records})

    # Initial partner registration, inserting primary details of partner
    @list_route(methods=['post'], url_path='partner-registration-step-one')
    def create_step_one_details(self, request):
        partner_detail = request.data

        partner_obj = InitialPartner()
        partner_obj.key = get_random_string(length=16)
        partner_obj.status = int(partner_detail['existing_partner'])
        partner_obj.jba_code = partner_detail['jba_code']
        partner_obj.registrations_status = 1
        partner_obj.existing_status = partner_detail['existing_partner']
        partner_obj.company_name = partner_detail['company_name']
        partner_obj.customer = 0
        partner_obj.save()

        domain = settings.DOMAIN_NAME
        if 'HTTP_ORIGIN' in request.META:
            domain = request.META['HTTP_ORIGIN']

        url_str = domain + '/' + partner_obj.key + '/registration/'

        try:
            # Inserting primary contact details of partner
            self.store_contact_details(partner_obj.id, 'P', partner_detail)
        except Exception:
            return Exception

        initial_partner_values = InitialPartner.objects.filter(id=partner_obj.id)
        serializer = InitialPartnerSerializer(initial_partner_values, many=True, context={'request': request})

        details = {
            'partner_detail': serializer.data[0],
            'url': url_str
        }

        try:
            send_mail_notifications.send(sender=InitialPartner, trigger='PartnerRegistration', details=details)
        except Exception:
            return Exception

        return Response(partner_obj.id)

    # Update partner primary details based on partner id
    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/partner-registration-step-one')
    def update_step_one_details(self, request, id):
        partner_detail = request.data

        partner_obj = InitialPartner.objects.filter(id=id)
        partner_obj.update(status=int(partner_detail['existing_partner']), company_name=partner_detail['company_name'],
                           existing_status=int(partner_detail['existing_partner']), jba_code=partner_detail['jba_code'])

        try:
            # Updating primary contact details of partner
            self.update_contact_details(id, 'P', partner_detail)
        except Exception:
            return Exception

        if partner_obj.first().customer:
            token = RedTokens.objects.filter(table_type=2, table_pkid=partner_obj.first().id)
            if token.exists():
                if token.first().status:
                    token.update(status=0)
                    domain = settings.DOMAIN_NAME
                    if 'HTTP_ORIGIN' in request.META:
                        domain = request.META['HTTP_ORIGIN']
                    url_str = domain + '/' + partner_obj.first().key + '/registration/'
                    serializer = InitialPartnerSerializer(partner_obj, many=True, context={'request': request})
                    details = {
                        'partner_detail': serializer.data[0],
                        'url': url_str
                    }

                    try:
                        send_mail_notifications.send(sender=InitialPartner, trigger='PartnerRegistration',
                                                     details=details)
                    except Exception:
                        return Exception

        return Response(True)

    # Update partner company, contact and document details, based on partner id
    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/partner-registration-step-two')
    def update_step_two_details(self, request, id):
        partner_detail = json.loads(request.data['partner_detail'])
        file_details = partner_detail['documents']
        files = request.FILES

        initial_partner_obj = InitialPartner.objects.filter(id=id)
        registration_status = 3 if initial_partner_obj.first() and initial_partner_obj.first().registration_status == 3\
            else 2
        initial_partner_obj.update(company_name=partner_detail['company_name'], address_1=partner_detail['addrs_line_1'],
                                   address_2=partner_detail['addrs_line_2'], address_3=partner_detail['addrs_line_3'],
                                   city=partner_detail['city'], state=partner_detail['state'],
                                   pin_code=partner_detail['pin_code'],
                                   preferred_user_name=partner_detail['preferred_user_name'],
                                   registration_status=registration_status, gst_number=partner_detail['gst_number'])

        try:
            if partner_detail['director_cntct_status']:
                director_detail_obj = {'name': partner_detail['director_name'],
                                       'email': partner_detail['director_email'],
                                       'mobile': partner_detail['director_mobile']}
                if InitialContactDetails.objects.filter(partner=id, type='D/O').exists():
                    # Calling the update contact details function to update contacts
                    self.update_contact_details(id, 'D/O', director_detail_obj)
                else:
                    # Calling the store contact details function to store contacts
                    self.store_contact_details(id, 'D/O', director_detail_obj)

            if partner_detail['accts_cntct_status']:
                accts_detail_obj = {'name': partner_detail['accts_name'],
                                       'email': partner_detail['accts_email'],
                                       'mobile': partner_detail['accts_mobile']}
                if InitialContactDetails.objects.filter(partner=id, type='A&O').exists():
                    self.update_contact_details(id, 'A&O', accts_detail_obj)
                else:
                    self.store_contact_details(id, 'A&O', accts_detail_obj)

            if partner_detail['sales_cntct_status']:
                sales_detail_obj = {'name': partner_detail['sales_name'],
                                    'email': partner_detail['sales_email'],
                                    'mobile': partner_detail['sales_mobile']}
                if InitialContactDetails.objects.filter(partner=id, type='S').exists():
                    self.update_contact_details(id, 'S', sales_detail_obj)
                else:
                    self.store_contact_details(id, 'S', sales_detail_obj)

        except Exception:
            return Exception

        try:
            # Calling the store files function to store documents
            self.store_files(id, file_details, files)
        except Exception:
            return Exception

        return Response(True)

    # Update partner business details, based on partner id
    @list_route(methods=['post'], url_path='(?P<id>[^/]+)/partner-registration-step-three')
    def update_step_three_details(self, request, id):
        partner_detail = request.data
        partner_type_str = None
        focused_customer_str = None
        interested_workloads_str = None

        for index, partner_type in enumerate(partner_detail['partner_type']):
            if index == 0:
                if partner_type:
                    partner_type_str = str(partner_type['id'])
            else:
                if partner_type:
                    if partner_type_str:
                        partner_type_str = partner_type_str+','+str(partner_type['id'])
                    else:
                        partner_type_str = str(partner_type['id'])

        for index, focused_customer in enumerate(partner_detail['focused_customer']):
            if index == 0:
                focused_customer_str = str(focused_customer['id'])
            else:
                focused_customer_str = focused_customer_str+','+str(focused_customer['id'])

        for index, interested_workloads in enumerate(partner_detail['interested_workloads']):
            if index == 0:
                interested_workloads_str = str(interested_workloads['id'])
            else:
                interested_workloads_str = interested_workloads_str+','+str(interested_workloads['id'])

        try:
            initial_partner_obj = InitialPartner.objects.filter(id=id)
            initial_partner_obj.update(registration_status=3, partner_type=partner_type_str,
                                       business_type=partner_detail['core_business'][0]['id'],
                                       focused_customer=focused_customer_str,
                                       interested_workload=interested_workloads_str)
        except Exception:
            return Exception

        initial_partner_values = InitialPartner.objects.filter(id=id)
        serializer = InitialPartnerSerializer(initial_partner_values, many=True, context={'request': request})

        try:
            send_mail_notifications.send(sender=InitialPartner, trigger='PartnerRequest', details=serializer.data[0])
        except Exception:
            return Exception

        return Response(True)

    # Getting registered partner details
    @list_route(methods=['get'], url_path='(?P<key>[^/]+)/registered_partner')
    def ger_registered_partner(self, request, key):
        if InitialPartner.objects.filter(key=key).exists():
            initial_partner_values = InitialPartner.objects.filter(key=key)
            serializer = InitialPartnerSerializer(initial_partner_values, many=True, context={'request': request})
            result = serializer.data[0]
        else:
            result = False

        return Response(result)

    # Storing contact details into database based on partner and type
    def store_contact_details(self, partner_id, detail_type, details):
        contact_obj = InitialContactDetails()
        contact_obj.partner = InitialPartner.objects.get(id=partner_id)
        contact_obj.type = detail_type
        contact_obj.name = details['name']
        contact_obj.email = details['email']
        contact_obj.mobile = details['mobile']
        contact_obj.save()

        return True

    # Update contact details based on partner and type
    def update_contact_details(self, partner_id, detail_type, details):
        contact_obj = InitialContactDetails.objects.filter(partner=partner_id, type=detail_type)
        contact_obj.update(name=details['name'], email=details['email'], mobile=details['mobile'])

        return True

    # Storing document details into database and directory based on partner and type
    def store_files(self, partner_id, file_details, files):
        for types in file_details:
            if types:
                if InitialDocumentDetails.objects.filter(type=types['type'], partner=partner_id).exists():
                    document_detail_obj = InitialDocumentDetails.objects.filter(type=types['type'], partner=partner_id)
                    # document_detail_obj.update(file_name=files[types['type']].name, file_data=files[types['type']])
                    document_detail_obj.delete()

                document_detail_obj = InitialDocumentDetails()
                document_detail_obj.type = types['type']
                document_detail_obj.file_name = files[types['type']].name
                document_detail_obj.file_data = files[types['type']]
                document_detail_obj.partner = InitialPartner.objects.get(id=partner_id)
                document_detail_obj.save()

        return True

    @list_route(methods=['get'], url_path='download_inactive_partner_list')
    def download_inactive_partner_list(self, request):
        queryset = self.queryset
        data = self.serializer_class(queryset, context={'request': request}, many=True).data
        # arrange data as we need
        for index, record in enumerate(data):
            data[index]['existing_status'] = 'Yes' if record['existing_status'] else 'No'
            data[index]['business_type'] = self.get_formatted_partner_business_type(record['business_type'])
            data[index]['focused_customer'] = self.get_formatted_customer_vertical(record['focused_customer'])
            data[index]['partner_type'] = self.get_formatted_partner_type(record['partner_type'])
            data[index]['interested_workload'] = self.get_formatted_partner_workload(record['interested_workload'])
            if not record['initial_contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['initial_contacts'][0]['name']
                data[index]['mobile'] = record['initial_contacts'][0]['mobile']
                data[index]['email'] = record['initial_contacts'][0]['email']

        from common.reports.ReportFieldMapping import ReportFieldMapping
        report_field_mapping = ReportFieldMapping()
        fields_options = report_field_mapping.createReport('in_active_partner_list')
        from common.reports.ReportList import ReportList
        return ReportList.exportCSVFile(self, data, fields_options, screename='inactive partner list')

    def get_formatted_partner_type(self,selected_values):
        formatted_string = ''
        if selected_values != '' and selected_values is not None:
            list_value = selected_values.split(',')
            from cloudapp.generics.constant import AppContants
            for index, key in enumerate(list_value):
                if index == 0:
                    if key == 'R':
                        key = '1'
                    formatted_string += AppContants.partner_Type[int(key) - 1]
                else:
                    if key == 'R':
                        key = '1'
                    formatted_string += ','+AppContants.partner_Type[int(key) - 1]
        return formatted_string

    def get_formatted_customer_vertical(self,selected_values):
        formatted_string = ''
        if selected_values != '' and selected_values is not None:
            list_value = selected_values.split(',')
            from cloudapp.generics.constant import AppContants
            for index, key in enumerate(list_value):
                if index == 0:
                    formatted_string += AppContants.partner_focused_customer[int(key) - 1]
                else:
                    formatted_string += ','+AppContants.partner_focused_customer[int(key) - 1]
        return formatted_string

    def get_formatted_partner_workload(self, selected_values):
        formatted_string = ''
        if selected_values != '' and selected_values is not None:
            list_value = selected_values.split(',')
            from cloudapp.generics.constant import AppContants
            for index, key in enumerate(list_value):
                if index == 0:
                    formatted_string += AppContants.partner_interested_workLoads[int(key) - 1]
                else:
                    formatted_string += ',' + AppContants.partner_interested_workLoads[int(key) - 1]
        return formatted_string

    def get_formatted_partner_business_type(self, selected_values):
        formatted_string = ''
        if selected_values != '' and selected_values is not None:
            list_value = selected_values.split(',')
            from cloudapp.generics.constant import AppContants
            for index, key in enumerate(list_value):
                if key == 'S':
                    key = '3'
                index_of_choices = int(key) - 1
                if index == 0:
                    formatted_string += AppContants.partner_core_business[index_of_choices]
                else:
                    formatted_string += ',' + AppContants.partner_core_business[index_of_choices]
        return formatted_string

    @list_route(methods=['get'], url_path='check-token-expired/(?P<token>[^/]+)/(?P<key>[^/]+)')
    def check_token_expired(self, request, token, key):
        if InitialPartner.objects.filter(key=key).exists():
            token = RedTokens.objects.filter(token=token, table_pkid=InitialPartner.objects.filter(key=key).first().id,
                                             table_type=2)
            if token.exists():
                return Response(token.first().status)

        return Response(False)


class AwsCreditsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = AwsCredits.objects.all()
    serializer_class = AwsCreditsSerializer

    @list_route(methods=['get'], url_path='list-partner-credits')
    def list_partner_credits(self, request, *args, **kwargs):
        partner_user = PartnerUserDetails.objects.get(user_id=request.user.id)
        partner_id = partner_user.partner_id
        query_set = self.queryset.filter(partner=partner_id)
        user = self.request.user

        value = self.get_aws_credits_records(request, query_set, user)

        return Response({'records': value['data'], 'totalRecords': value['total_records']})

    @list_route(methods=['get'], url_path='list-all-credits')
    def list_all_credits(self, request, *args, **kwargs):
        query_set = self.queryset
        user = self.request.user

        value = self.get_aws_credits_records(request, query_set, user)

        return Response({'records': value['data'], 'totalRecords': value['total_records']})

    def get_aws_credits_records(self, request, query_set, user):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        searchText = query_params.pop('searchText', None)

        if searchText is not None:
            query_set = query_set.filter(
                Q(partner__company_name__icontains=searchText)
            ).distinct()

        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data

        for index, record in enumerate(data):
            coupon_code = record['coupon_code']
            total_value = AwsCredits.history.get(coupon_code=coupon_code, history_type='+').value
            # add currency format to credit limit
            from cloudapp.generics.functions import currencyFormat
            data[index]['current_value'] = currencyFormat(record['value'], 2)
            data[index]['total_value'] = currencyFormat(total_value, 2)
            if record['value'] == '0.00':
                data[index]['fully_applied'] = 'YES'
            else:
                data[index]['fully_applied'] = 'NO'

        value = {'data': data, 'total_records': total_records}

        return value

    @list_route(methods=['post'], url_path='add-partner-credit')
    def add_partner_credit(self, request, *args, **kwargs):
        data = request.data
        if data['user_type'] == 'P':
            partner_user = PartnerUserDetails.objects.get(user_id=request.user.id)
            partner_id = partner_user.partner_id
        else:
            partner_id = data['partner_id']

        partner_object = Partner.objects.get(id=partner_id)
        value = 0.00
        if data['value']:
            value = data['value']

        aws_credit_object = AwsCredits()
        aws_credit_object.partner = partner_object
        aws_credit_object.coupon_code = data['coupon_code']
        aws_credit_object.value = value
        aws_credit_object.customer = data['customer']
        aws_credit_object.created_by = request.user
        aws_credit_object.created_date = timezone.now()

        if data['expiry_date']:
            aws_credit_object.expiry_date = data['expiry_date']
        aws_credit_object.save()

        if data['user_type'] == 'P':
            send_mail_notifications.send(sender=Partner, trigger='CreditsUpdated', details={'user': request.user, 'partner_details': partner_object })

        return Response(True)

    @list_route(methods=['get'], url_path='get-aws-credits/(?P<id>[^/]+)')
    def get_aws_credits(self, request, id, *args, **kwargs):
        credit_id = id
        queryset = AwsCredits.objects.filter(id=credit_id)
        aws_credits_value = list(queryset.values())

        query_set = CloudAccounts.objects.filter(type='AWS', customer_id=aws_credits_value[0]['customer']).first()
        value = CloudAccountsSerializer(query_set, context={'request': request}).data

        data = {'id': value['id'],
                'account_id': value['details']['account_id'],
                'customer_id': value['customer_details']['id'],
                'company_name': value['customer_details']['company_name'],
                'customer_details': value['customer_details'],
                'iam_details': value['details']}

        aws_credits_value[0]['customer'] = data

        return Response({'awsCreditdetails': aws_credits_value})

    @list_route(methods=['post'], url_path='update-aws-credits/(?P<id>[^/]+)')
    def update_customer(self, request, id, *args, **kwargs):
        data_val = request.data['value']
        data = json.loads(data_val)

        aws_credit_object = AwsCredits.objects.get(id=id)
        aws_credit_object.coupon_code = data['coupon_code']
        aws_credit_object.value = data['value']
        aws_credit_object.expiry_date = data['expiry_date']
        aws_credit_object.customer = data['customer']
        aws_credit_object.modified_by = request.user
        aws_credit_object.modified_date= timezone.now()

        aws_credit_object.save()

        return Response(True)

    @list_route(methods=['post'], url_path='get-aws-customers')
    def get_aws_customers(self, request, *args, **kwargs):
        partner_user = PartnerUserDetails.objects.filter(user_id=request.user.id).values()
        if partner_user:
            partner_id = partner_user[0]['partner_id']
        else:
            partner_id = ''

        query_params = request.query_params.dict()
        search_text = request.data['search_text']

        query_set = CloudAccounts.objects.filter(type='AWS', customer__company_name__icontains=search_text, active=True)

        if partner_id != '':
            query_set = query_set.filter(customer__partner=partner_id)

        values = CloudAccountsSerializer(query_set, context={'request': request}, many=True).data
        data = []
        for value in values:
            data.append(value['customer_details'])

        return Response(data)

    @list_route(methods=['post'], url_path='get-aws-linked-customers')
    def get_aws_linked_customers(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        search_text = request.data['search_text']

        query_set = CloudAccounts.objects.filter(type='AWS', details__account_id__contains=search_text, active=True)

        values = CloudAccountsSerializer(query_set, context={'request': request}, many=True).data
        data = []
        for value in values:
            details = {'id': value['id'],
                       'account_id': value['details']['account_id'],
                       'customer_id': value['customer_details']['id'],
                       'company_name': value['customer_details']['company_name'],
                       'customer_details': value['customer_details'],
                       'iam_details': value['details']}
            data.append(details)

        return Response(data)

    @list_route(methods=['get'], url_path='get-aws-linked-customer/(?P<id>[^/]+)')
    def get_aws_linked_customer(self, request, id, *args, **kwargs):
        query_set = CloudAccounts.objects.filter(id=id)

        value = CloudAccountsSerializer(query_set, context={'request': request}, many=True).data[0]
        data = {'id': value['id'],
                   'account_id': value['details']['account_id'],
                   'customer_id': value['customer_details']['id'],
                   'company_name': value['customer_details']['company_name'],
                   'customer_details': value['customer_details'],
                   'iam_details': value['details']}

        return Response(data)

    @list_route(methods=['post'], url_path='check-coupon-code')
    def check_coupon_code(self, request, *args, **kwargs):
        coupon_code = request.data['coupon_code']
        queryset = AwsCredits.objects.filter(coupon_code=coupon_code)
        querysetlength = len(queryset)
        return Response(querysetlength)


class RejectedPartnerViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = InitialPartner.objects.filter(registration_status=4)
    serializer_class = InitialPartnerSerializer

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        company_name = query_params.pop('company_name', None)
        order_by = query_params.pop('order_by', None)
        searchText = query_params.pop('searchText', None)
        query_set = self.queryset

        if searchText is not None:
            query_set = query_set.filter(Q(company_name__icontains=searchText) |
                                         Q(city__icontains=searchText) |
                                         Q(initial_contacts__email__icontains=searchText)
                                         ).distinct()
        if company_name is not None:
            query_set = query_set.filter(company_name__icontains=company_name)
        if order_by is not None:
            query_set = query_set.order_by(order_by)

        query_set = query_set.filter(customer=0)
        total_records = query_set.count()
        query_set = query_set[offset:end]
        data = self.serializer_class(query_set, context={'request': request}, many=True).data
        for index, record in enumerate(data):
            if not record['initial_contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
            else:
                data[index]['name'] = record['initial_contacts'][0]['name']
                data[index]['mobile'] = record['initial_contacts'][0]['mobile']
                data[index]['email'] = record['initial_contacts'][0]['email']
        return Response({'records': data, 'totalRecords': total_records})

    @list_route(methods=['post'], url_path='view-reason')
    def get_reject_reason(self,request, *args, **kwargs):
        partner_id = request.data['partner_id']
        query_set = PartnerRejections.objects.values().filter(partner_id=partner_id)
        return Response(query_set)

    @list_route(methods=['post'], url_path='delete-partner')
    def delete_partner(self, request, *args, **kwargs):
        partner_id = request.data['partner_id']
        initial_partner_obj = InitialPartner.objects.values().filter(id=partner_id)
        initial_partner_obj.update(registration_status=0)
        return Response(True)



    @list_route(methods=['get'], url_path='download-rejected-partner-export-excel')
    def download_rejected_partner_list(self, request):
        queryset = self.queryset
        query_set = queryset.filter(customer=0)
        data = self.serializer_class(query_set, context={'request': request}, many=True).data
        # arrange data as we need
        inital_view_set = InitialPartnerViewSet()
        for index, record in enumerate(data):
            data[index]['existing_status'] = 'Yes' if record['existing_status'] else 'No'
            data[index]['business_type'] = inital_view_set.get_formatted_partner_business_type(record['business_type'])
            data[index]['focused_customer'] = inital_view_set.get_formatted_customer_vertical(record['focused_customer'])
            data[index]['partner_type'] = inital_view_set.get_formatted_partner_type(record['partner_type'])
            data[index]['interested_workload'] = inital_view_set.get_formatted_partner_workload(record['interested_workload'])
            if not record['initial_contacts']:
                data[index]['name'] = ''
                data[index]['mobile'] = ''
                data[index]['email'] = ''
                data[index]['email_1'] = ''
                data[index]['email_2'] = ''
                data[index]['email_3'] = ''
            else:
                data[index]['name'] = record['initial_contacts'][0]['name']
                data[index]['mobile'] = record['initial_contacts'][0]['mobile']
                data[index]['email'] = record['initial_contacts'][0]['email']
                if len(record['initial_contacts']) == 4:
                    data[index]['email_1'] = record['initial_contacts'][1]['email']
                    data[index]['email_2'] = record['initial_contacts'][2]['email']
                    data[index]['email_3'] = record['initial_contacts'][3]['email']
                else:
                    data[index]['email_1'] = ''
                    data[index]['email_2'] = ''
                    data[index]['email_3'] = ''

        from common.reports.ReportFieldMapping import ReportFieldMapping
        report_field_mapping = ReportFieldMapping()
        fields_options = report_field_mapping.createReport('rejected_partner_list')
        from common.reports.ReportList import ReportList
        file_generator = ReportList()
        return file_generator.exportEXCELFile(data_list=data, screen_name='product list',
                                              field_mappings=fields_options)
