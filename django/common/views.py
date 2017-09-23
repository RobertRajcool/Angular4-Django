from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from django.db import connection
from cloudapp.generics.query_manager import dictfetchall
from common.models import AipDirectory, RedTokens, ConversionRates, PartnerFeedback
from common.serializers import AipDirectorySerializer, ConversionRatesSerializer, PartnerFeedbackSerializer
from customers.models import Customers, CustomerContacts
from users.models import RedUser
import uuid
from cloudapp.generics.functions import generate_feedback_number
from django.utils.decorators import method_decorator
from rest_framework import permissions
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.core.mail import EmailMessage
from common.signals import send_mail_notifications


class AipDirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AipDirectorySerializer
    queryset = AipDirectory.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset[:25]
        serializer = AipDirectorySerializer(queryset, context={'request': request}, many=True)

        return Response(serializer.data)

    @list_route(methods=['get'], url_path="filter")
    def filter_districts(self, request, **kwargs):
        query_params = request.query_params.dict()
        typo = query_params.pop('typo', '')
        filter_by = query_params.pop('filter_by', 'pincode')
        limit = 15
        query = '''SELECT `id`, `pincode`, `district`, `state` FROM `common_aipdirectory`'''
        cursor = connection.cursor()
        queryset = []

        if filter_by == 'pincode':
            query += '''WHERE  `pincode` LIKE "%%%s%%" GROUP BY `pincode` ORDER BY `pincode` ASC LIMIT %d''' % (
                typo, limit)
            cursor.execute(query)
            queryset = dictfetchall(cursor)
        elif filter_by == 'district':
            query += '''WHERE  `district` LIKE "%%%s%%" GROUP BY `district` ORDER BY `district` ASC LIMIT %d''' % (
                typo, limit)
            cursor.execute(query)
            queryset = dictfetchall(cursor)
        elif filter_by == 'state':
            query += '''WHERE  `state` LIKE "%%%s%%" GROUP BY `state` ORDER BY `state` ASC LIMIT %d''' % (
                typo, limit)
            cursor.execute(query)
            queryset = dictfetchall(cursor)

        return Response(queryset)

class RedTokenViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)

    def generate_token(self, table_type, table_pkid):
        """ Function to create new Token """
        token = str(uuid.uuid1())
        token_object = RedTokens()
        token_object.table_type = table_type
        token_object.table_pkid = table_pkid
        token_object.token = token
        token_object.save()
        return token

    def check_token_exist(self, customer_id):
        """ Function to check whether we send create link already """
        tokens = list(RedTokens.objects.filter(table_pkid=customer_id))
        token_id = ''
        if len(tokens):
            token = tokens[0]
            if token.status:
                from datetime import datetime
                import datetime as nd
                current_date = datetime.now()
                end_date = current_date + nd.timedelta(days=7)
                token.expiry_date = end_date
                token.save()
                token_id = token.token
            else:
                token_id = 'do_not_send'
        else:
            token_id = self.generate_token(1, customer_id)
        return token_id

    @list_route(methods=['post'], url_path='authenticate')
    def authenticate(self, request, **kwargs):
        from django.utils import timezone
        form_data = request.data
        is_valid = False
        if 'token' in form_data.keys() and form_data['token'] != '':
            token_query_set = RedTokens.objects.filter(token=form_data['token'], expiry_date__gt=timezone.now(),
                                                       status=True)
            token_data = list(token_query_set.values())
            if len(token_data) > 0:
                is_valid = True
        return Response(is_valid)



class ConversionRatesViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ConversionRatesSerializer
    queryset = ConversionRates.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset[:25]
        serializer = ConversionRatesSerializer(queryset, context={'request': request}, many=True)

        return Response(serializer.data)


class PartnerFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PartnerFeedbackSerializer
    queryset = PartnerFeedback.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset[:25]
        serializer = PartnerFeedbackSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        feedback_object = PartnerFeedback()
        feedback_object.feedback_number = generate_feedback_number()
        feedback_object.reason = request.data['reason']
        feedback_object.description = request.data['description']
        feedback_object.name = request.data['name']
        feedback_object.email = request.data['email']
        feedback_object.mobile = request.data['mobile']
        feedback_object.created_by = request.user
        if 'attachment' in request.FILES:
            feedback_object.attachment = request.FILES['attachment']
        feedback_object.save()
        send_mail_notifications.send(sender=PartnerFeedback, trigger='PartnerFeedback',
                                     details={'user': request.user, 'feedback_details': feedback_object})
        return Response(True)

class IsvFeedbackViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PartnerFeedbackSerializer
    queryset = PartnerFeedback.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.queryset[:25]
        serializer = PartnerFeedbackSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        feedback_object = PartnerFeedback()
        feedback_object.feedback_number = generate_feedback_number()
        feedback_object.reason = request.data['reason']
        feedback_object.description = request.data['description']
        feedback_object.name = request.data['name']
        feedback_object.email = request.data['email']
        feedback_object.mobile = request.data['mobile']
        feedback_object.created_by = request.user
        if 'attachment' in request.FILES:
            feedback_object.attachment = request.FILES['attachment']
        feedback_object.save()
        send_mail_notifications.send(sender=PartnerFeedback, trigger='IsvFeedback',
                                     details={'user': request.user, 'feedback_details': feedback_object})
        return Response(True)