from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.views import Response
from rest_framework import status, permissions
from rest_framework.decorators import detail_route, list_route
import math
from notifications.models import Notifications, NotificationGroups, NotificationActions
from notifications.serializers import NotificationsSerializer, NotificationGroupsSerializer, \
    NotificationActionsSerializer
from notifications.generics.notifications import NfActions
from cloudapp.defaults import AppDefaults


class NotificationsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationsSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Notifications.objects.filter(recipients__regex=r'^{0},|,{0},|,{0}$|^{0}$'.format(user.id))
        return queryset

    @list_route(methods=['get'], url_path='filter')
    def get_page_list(self, request, filters=None, **kwrgs):

        if filters is None:
            filters = request.query_params.dict()

        exclude_filters = {}
        data = {}
        page = int(filters.pop('page_number', 1))
        records_per_page = int(filters.pop('records_per_page', 10))
        record_count = records_per_page
        last_record = data['last_record'] = page * record_count
        first_record = data['first_record'] = last_record - record_count

        # Reformat notification type
        if filters['type'] == 'alerts':
            filters['type'] = 'A'
        elif filters['type'] == 'messages':
            filters['type'] = 'M'

        # Reformat notification status
        if filters['status'] == 'unread':
            exclude_filters['viewed_by__contains'] = request.user.id
        elif filters['status'] == 'read':
            filters['viewed_by__contains'] = request.user.id
        elif filters['status'] == 'pending':
            filters['completed_by__isnull'] = True
        elif filters['status'] == 'completed':
            filters['completed_by__isnull'] = False
        del filters['status']

        queryset = self.get_queryset().order_by('-posted_at')
        data['total_unread_messages'] = queryset.filter(type='M').exclude(viewed_by__contains=request.user.id).count()
        data['total_unread_alerts'] = queryset.filter(type='A').exclude(viewed_by__contains=request.user.id).count()
        queryset = queryset.filter(type=filters['type'])
        del filters['type']
        data['total_pending'] = queryset.filter(completed_by__isnull=True).count()
        data['total_completed_unread'] = queryset.filter(completed_by__isnull=False).exclude(
            viewed_by__contains=request.user.id).count()

        filtered_set = queryset.filter(**filters).exclude(**exclude_filters)
        # Query for notifications count
        data['total_filtered_nf'] = filtered_set.count()
        data['total_filtered_pages'] = math.ceil(data['total_filtered_nf'] / records_per_page)
        # Query for page data
        queryset = filtered_set[first_record:last_record]
        data['notifications'] = self.serializer_class(queryset, context={'request': request}, many=True).data

        return Response(data)

    @detail_route(methods=['post'], url_path='mark-as-read')
    def mark_notification_as_read(self, request, **kwrgs):
        notification = NfActions.mark_as_read({
            'nf_id': kwrgs['pk'],
            'user': request.user
        })

        return self.get_page_list(request, filters=request.data['filters'], **kwrgs)

    @detail_route(methods=['get'], url_path='mark-as-completed')
    def mark_notification_as_completed(self, request, **kwrgs):
        notification = NfActions.complete({
            'nf_id': kwrgs['pk'],
            'user': request.user
        })

        data = NotificationsSerializer(notification, context={'request': request}).data

        return Response(data)


@method_decorator(permission_required('notificationgroups.list_notificationgroups', raise_exception=True), name='list')
@method_decorator(permission_required('notificationgroups.view_notificationgroups', raise_exception=True), name='retrieve')
@method_decorator(permission_required('notificationgroups.add_notificationgroups', raise_exception=True), name='create')
@method_decorator(permission_required('notificationgroups.change_notificationgroups', raise_exception=True), name='update')
@method_decorator(permission_required('notificationgroups.change_notificationgroups', raise_exception=True), name='partial_update')
@method_decorator(permission_required('notificationgroups.delete_notificationgroups', raise_exception=True), name='destroy')
class NotificationGroupsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationGroupsSerializer

    def get_queryset(self):
        queryset = NotificationGroups.objects.filter(deleted=False)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        primary_keys = [str(r['id']) for r in data['recipients']]
        data['recipients'] = ','.join(primary_keys)
        if data['non_user_recipients'] == '':
            data['non_user_recipients'] = []
        request._data = data

        return super(NotificationGroupsViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        data = request.data
        primary_keys = [str(r['id']) for r in data['recipients']]
        data['recipients'] = ','.join(primary_keys)
        if data['non_user_recipients'] == '':
            data['non_user_recipients'] = []
        request._data = data

        return super(NotificationGroupsViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.deleted_by = request.user
        instance.actions.clear()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(permission_required('notificationactions.list_notificationactions', raise_exception=True), name='list')
@method_decorator(permission_required('notificationactions.view_notificationactions', raise_exception=True), name='retrieve')
class NotificationActionsViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationActionsSerializer

    def get_queryset(self):
        queryset = NotificationActions.objects.all()
        return queryset

    @method_decorator(permission_required('notificationactions.view_notificationactions', raise_exception=True),
                      name='fetch_action_details')
    @list_route(methods=['get'], url_path='(?P<action>[0-9A-Za-z_.]+)/fetch-details')
    def fetch_action_details(self, request, *args, **kwargs):
        action = kwargs['action']
        if action == 'initial':
            action = AppDefaults.get_notification_signals()[0][0]

        queryset = self.get_queryset().filter(action=action)
        response = {
            'action_details': None
        }
        if len(queryset) > 0:
            response['action_details'] = self.serializer_class(queryset[0], context={'request': request}).data

        response['actions'] = AppDefaults.get_notification_signals()
        response['unmapped_groups'] = list(
            NotificationGroups.objects.filter(deleted=False).exclude(actions__action=action).values('id', 'name'))
        return Response(response)

    @method_decorator(permission_required('notificationactions.add_notificationactions', raise_exception=True),
                      name='map_group')
    @method_decorator(permission_required('notificationactions.change_notificationactions', raise_exception=True),
                      name='map_group')
    @list_route(methods=['post'], url_path='map-group')
    def map_group(self, request, **kwargs):
        action = request.data['action']
        group_id = request.data['group_id']

        nf_action = self.get_queryset().filter(action=action)
        if len(nf_action) == 0:  # Creating action if not created before
            nf_action = NotificationActions.objects.create(action=action, created_by=request.user, modified_by=request.user)
            nf_action.save()
        else:  # If already created, gets the actions
            nf_action = nf_action[0]
            nf_action.modified_by = request.user

        nf_action.groups.add(NotificationGroups.objects.get(id=group_id))
        nf_action.save()

        return self.fetch_action_details(request=request, action=action)

    @method_decorator(permission_required('notificationactions.change_notificationactions', raise_exception=True),
                      name='unmap_group')
    @list_route(methods=['post'], url_path='unmap-group')
    def unmap_group(self, request, **kwargs):
        action_id = request.data['action_id']
        group_id = request.data['group_id']

        nf_action = self.get_queryset().get(id=action_id)
        nf_action.groups.remove(NotificationGroups.objects.get(id=group_id))
        nf_action.modified_by = request.user
        nf_action.save()

        return self.fetch_action_details(request=request, action=nf_action.action)
