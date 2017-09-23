
import requests
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from users.models import RedUser, USER_TYPE_CHOICES, PasswordResetTokens
from users.serializers import UsersSerializer, GroupSerializer
from django.db.models import Q
from cloudapp.defaults import AppDefaults
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
import datetime
from common.mails.BaseMails import BaseMails
from common.signals import send_mail_notifications
from django.utils.crypto import get_random_string
from partner.models import Partner, PartnerUserDetails
import collections
from common.custom_exceptions import RedValidationErr

from setuptools.package_index import unique_everseen


def jwt_response_payload_handler(token, user=None, request=None):
    """ Modifying jwt login response details """
    user_details = UsersSerializer(user, context={'request': request}).data

    """ Fetching assigned accesses for the use """
    user_details['accesses'] = list()

    if user.is_superuser:
        user_details['accesses'] = AppDefaults.get_predefined_role_access_specifiers('Admin')
    else:
        access_joined = user.groups.all().values_list('details__accesses', flat=True)
        for string in access_joined:
            if string is not None:
                user_details['accesses'] += string.split(',')
        user_details['accesses'] = list(set(user_details['accesses']))

    user_details['accesses'] = sorted(user_details['accesses'])

    return {
        'token': token,
        'user': user_details
    }


@method_decorator(permission_required('users.list_reduser', raise_exception=True), name='list')
@method_decorator(permission_required('users.view_reduser', raise_exception=True), name='retrieve')
@method_decorator(permission_required('users.add_reduser', raise_exception=True), name='create')
@method_decorator(permission_required('users.change_reduser', raise_exception=True), name='update')
@method_decorator(permission_required('users.change_reduser', raise_exception=True), name='partial_update')
@method_decorator(permission_required('users.delete_reduser', raise_exception=True), name='destroy')
class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = RedUser.objects.all()
    serializer_class = UsersSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = RedUser.objects.all()
        if user.is_superuser == True:
            query_set = queryset.filter(~Q(profile__user_type='P'))
        elif user.profile.user_type == 'R':
            query_set = queryset.filter(~Q(profile__user_type='P'))
        else:
            query_set = queryset.filter(profile__created_by=user)
        return query_set

    @method_decorator(permission_required('users.add_reduser', raise_exception=True), name='create')
    def create(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.id
        password = get_random_string(length=7)
        request.data['password'] = password

        user = super(self.__class__, self).create(request, *args, **kwargs)
        user_id = user.data['id']

        u = RedUser.objects.get(pk=user_id)
        u.set_password(password)
        u.save()

        try:
            details = {
                'user_detail': user.data,
                'password': password
            }
            send_mail_notifications.send(sender=RedUser, trigger='UserCreation', details=details)
        except Exception:
            return Exception

        return user

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.dict()
        offset = int(query_params.pop('offset', 0))
        end = int(query_params.pop('end', 5))
        queryset = self.get_queryset().filter(is_active=1).exclude(username='AnonymousUser')
        order_by = query_params.pop('order_by', None)
        search_text = query_params.pop('searchText', None)
        query_set = queryset

        if search_text is not None:
            query_set = query_set.filter(
                Q(first_name__icontains=search_text) |
                Q(email__icontains=search_text) |
                Q(last_name__icontains=search_text))
        if order_by is not None:
            if order_by == 'full_name' or order_by == '-full_name':
                order_by = order_by.replace('full_name', 'first_name')
            query_set = query_set.order_by(order_by)
        total_records = query_set.filter(is_active=1).count()
        query_set = query_set[offset:end]
        serializer = UsersSerializer(query_set, many=True, context={'request': request})
        data = serializer.data
        user_types = dict(USER_TYPE_CHOICES)
        for index, record in enumerate(data):
            if record['user_type']:
                data[index]['user_type'] = user_types[record['user_type']]
        return Response({'records': serializer.data, 'totalRecords': total_records})

    @list_route(methods=['post'], url_path='user-view')
    def getuser(self, request, *args, **kwargs):
        userId = request.data['id']
        queryset = self.get_queryset().filter(id=userId)
        serializer = UsersSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='delete/(?P<id>[^/]+)')
    def delete(self, request, id):
        query = self.get_queryset().filter(id=id).update(is_active=0)
        queryset = self.get_queryset().filter(is_active=1)
        serializer = UsersSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['post'], url_path='check-username')
    def check_user_list(self, request, *args, **kwargs):
        user_name = request.data['username']
        queryset = RedUser.objects.filter(username=user_name)
        querysetlength = len(queryset);
        return Response(querysetlength)

    @list_route(methods=['post'], url_path='user-getEmployeeDetails')
    def get_api_employeedetails(self, request, *args, **kwargs):
        employee_code = request.data['employe_id']
        response = requests.get(
            "http://edi.redingtonb2b.in/RedCloudStaging/api/RedingtonCloudApi/GetEmployee?EmployeeCode=" + (
                employee_code))
        json_data = response.json()
        Employee_details = [b for b in json_data]
        if len(Employee_details) != 0:
            employee_name = Employee_details[0]['EmpNam']
            emp = employee_name.split(' ')
            if len(emp)>0:
                employee_firstname = (emp[0])
            else:
                employee_firstname=''
            if len(emp) >1:
                employee_lastname = (emp[1])
            else:
                employee_lastname =''
            employee_email = Employee_details[0]['EmpEmail']
            vendorname_array = []
            vendorsList = list(set(list(map(lambda x: x['BizDesc'], Employee_details))))
            if 'MSCL - Microsoft Cloud' in vendorsList:
                vendorsList.append('MSCL - AZURE')
            vendorname = collections.OrderedDict()
            employee_branch_code=collections.OrderedDict()
            for vendor in vendorsList:
                jba_name = vendor[:4]
                temp = list(filter(lambda x: x['BizDesc'] == vendor, Employee_details))
                if temp != []:
                    vendorname[vendor] = list(set(list(map(lambda x: x['BranchDesc'], temp)))) if temp[0][
                                                                                                   'BranchDesc'] != 'Corporate' else 'Corporate'
                    employee_branch_code[vendor]= list(set(list(map(lambda x: x['BranchCode'], temp)))) if temp[0][
                                                                                                      'BranchCode'] != 'CO' else 'CO'

                else:
                    vendorname[vendor] = 'Corporate'

            cleanlist = []
            [cleanlist.append(x) for x in vendorname_array if x not in cleanlist]

            return Response({
                'employeename': employee_name,
                'employeeEmail': employee_email,
                'employee_firstname': employee_firstname,
                'employee_lastname': employee_lastname,
                'employee_code': employee_code,
                'employee_region': vendorname,
                'vendor_details': cleanlist,
                'employee_branch_code':employee_branch_code
            })
        else:
            return Response(Employee_details)

    @list_route(methods=['get'], url_path='check_user/(?P<source>[^/]+)')
    def checkUser(self, request, source):
        query = self.get_queryset().filter(username=source)
        serializer = UsersSerializer(query, many=True, context={'request': request})
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='user_type')
    def get_user_type(self, request):

        user_name = request.user.username
        queryset = RedUser.objects.filter(username=user_name)
        serializer = UsersSerializer(queryset, many=True, context={'request': request})
        user_type = serializer.data[0]['user_type']
        super_user = serializer.data[0]['is_superuser']
        if (user_type == 'R' or super_user == True):
            USER_TYPE_CHOICES = [{'id': 'R', 'text': 'Redington'},{'id': 'RI', 'text': 'ISV Manager'}]
        else:
            USER_TYPE_CHOICES = [{'id': 'P', 'text': 'Partner'},
                                 {'id': 'C', 'text': 'Customer'}
                                 ]

        return Response(USER_TYPE_CHOICES)

    @list_route(methods=['post'], url_path='search')
    def search_user(self, request, **kwargs):
        search_text = request.data['search_text']
        search_field = request.data['search_field']
        must_filters = dict()
        should_filters = dict()
        must_filters['profile__user_type__in'] = ['R', 'RI']

        if search_field == 'first_name + last_name':
            should_filters['first_name__icontains'] = should_filters['last_name__icontains'] = search_text
        else:
            should_filters['%s__icontains' % search_field] = search_text

        def dict_to_query(dictionary, operator):
            q = None
            for k, v in dictionary.items():
                if operator == 'AND':
                    q = q & Q(**{k: v}) if q else Q(**{k: v})
                elif operator == 'OR':
                    q = q | Q(**{k: v}) if q else Q(**{k: v})

            return q

        queryset = self.get_queryset().filter(dict_to_query(must_filters, 'AND') &
                                              dict_to_query(should_filters, 'OR'))[:10]
        data = UsersSerializer(queryset, context={'request': request}, many=True).data

        return Response(data)

    @list_route(methods=['get'], url_path='user-partner-details/(?P<id>[^/]+)')
    def get_user_partner_details(self, request, id):
        partner_user_obj = PartnerUserDetails.objects.filter(user=id).exists()
        partner_id = ''
        if partner_user_obj:
            partner_id = PartnerUserDetails.objects.get(user=id).partner_id

        return Response(partner_id)

    @list_route(methods=['post'], url_path='change-password')
    def change_password(self, request):
        user = self.request.user
        old_password = request.data['old_password']
        from django.contrib.auth import authenticate
        credentials = {
           'username': user.username,
           'password': old_password
        }
        user = authenticate(**credentials)
        if user:
            user.set_password(request.data['password'])
            user.save()
            BaseMails.send_mail(
                subject='REDINGTON: Password changed',
                recipients=[user.email],
                template_name='password_changed.html',
                template_data={
                    'user': user.__dict__
                }
            )
            return Response({'suc_msg': "Your Password changed"})
        else:
            return Response({'msg': "Your old password was entered incorrectly"})


@method_decorator(permission_required('auth.list_group', raise_exception=True), name='list')
@method_decorator(permission_required('auth.view_group', raise_exception=True), name='retrieve')
@method_decorator(permission_required('auth.add_group', raise_exception=True), name='create')
@method_decorator(permission_required('auth.change_group', raise_exception=True), name='update')
@method_decorator(permission_required('auth.change_group', raise_exception=True), name='partial_update')
@method_decorator(permission_required('auth.delete_group', raise_exception=True), name='destroy')
class GroupsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = None
        if user.is_superuser:
            queryset = Group.objects.filter(~Q(details__alias='Partner'),
                                            (Q(details__created_by=user) | Q(details__created_by=None)))
        else:
            queryset = Group.objects.filter(details__created_by=user)
        return queryset.order_by('details__alias')


class PasswordReset(APIView):
    """ Generates password reset token and reset link """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        data = request.data

        """ Checking is user exists for the provided username """
        if not RedUser.objects.filter(username=data['username']).exists():
            raise RedValidationErr("Username doesn't exists.")

        user = RedUser.objects.get(username=data['username'])

        """ Verifying users email """
        if user.email != data['email']:
            email = user.email

            last = len(user.email) - 1
            at_sign_position = email.index('@')
            dot_position = email.index('.')

            email_hint = '%s%s%s%s%s' % (
                email[0:2],
                '*' * len(email[2:at_sign_position]),
                email[at_sign_position:(at_sign_position + 2)],
                '*' * (dot_position - (at_sign_position + 2)),
                email[dot_position:(last + 1)]
            )
            raise RedValidationErr("Email couldn't match with username. Hint: %s" % email_hint)

        """ Generating token for password reset link """
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        """ Setting expiration time """
        payload['exp'] = datetime.datetime.now() + datetime.timedelta(days=1)
        token = jwt_encode_handler(payload)

        """ Storing token for future reference """
        session = PasswordResetTokens.objects.create(user=user, token=token)
        session.save()

        BaseMails.send_mail(
            subject='REDINGTON: Password reset link',
            recipients=[user.email],
            template_name='password_resetting.html',
            template_data={
                'user': user.__dict__,
                'reset_link': '%s?tk=%s' % (data['base_path'], token)
            }
        )

        return Response({'msg': "Reset link sent successfully", 'email': user.email})


class PasswordResetVerify(APIView):
    """ Verifies password reset token """
    permission_classes = (permissions.AllowAny,)
    serializer_class = VerifyJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if PasswordResetTokens.objects.filter(token=data['token']).exists():
                return Response(data['token'])
            else:
                raise RedValidationErr('It seems that link has been used already.')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirm(APIView):
    """ Changes user password """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        """ Updating password """
        user.set_password(data['password'])
        user.save()

        """ Removing token from password reset session after changing password """
        session = PasswordResetTokens.objects.filter(user=user)
        session.delete()

        BaseMails.send_mail(
            subject='REDINGTON: Password changed',
            recipients=[user.email],
            template_name='password_changed.html',
            template_data={
                'user': user.__dict__
            }
        )

        serializer = UsersSerializer(user, context={'request': request})
        return Response(serializer.data)

api_password_reset = PasswordReset.as_view()
api_password_reset_verify = PasswordResetVerify.as_view()
api_password_reset_confirm = PasswordResetConfirm.as_view()
