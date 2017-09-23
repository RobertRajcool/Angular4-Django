from notifications.models import Notifications
import datetime


class NfActions:
    @classmethod
    def publish(cls, params):
        """
            Publishing new notification....

            The required params properties & formats:
                {
                    'user': request.user,
                    'nf_type': "message" or "alert",
                    'recipients': Recipients as comma seperated string i.e "1,4,2",
                    'message': Notification message,
                    'status': Notification status,
                    'details_obj': The model object for which notification has to be created
                }
        """
        params['recipients'] = params['recipients'].split(',')
        params['recipients'] = ','.join(list(set(params['recipients'])))

        params['nf_type'] = 'M' if params['nf_type'] == 'message' else 'A'
        nf = Notifications.objects.create(
            posted_by=params['user'],
            type=params['nf_type'],
            recipients=params['recipients'],
            purpose=params['message'],
            status=params['status'],
            details=params['details_obj'],
            posted_at=datetime.datetime.now()
        )

        nf.save()
        return nf

    @classmethod
    def mark_as_read(cls, params):
        """
            Marking notification as read by the user....

            The required params properties & formats:
                {
                    'nf_id': id of notification,
                    'user': request.user
                }

        """
        nf = Notifications.objects.get(id=params['nf_id'])

        viewed_by = nf.viewed_by
        user_id = str(params['user'].id)
        if viewed_by is None or viewed_by == "":
            viewed_by = user_id
        else:
            viewed_by = viewed_by.split(',')
            if user_id not in viewed_by:
                viewed_by.append(user_id)
            viewed_by = ','.join(viewed_by)

        nf.viewed_by = viewed_by
        nf.save()

        return nf

    @classmethod
    def complete(cls, params):
        """
            Completing notification....

            The required params properties & formats:
                {
                    'nf_id': id of notification,
                    'user': request.user
                }

        """
        nf = Notifications.objects.get(id=params['nf_id'])
        viewed_by = nf.viewed_by.split(',') if nf.viewed_by is not None else []
        viewed_by.append(str(params['user'].id))
        viewed_by = ','.join(viewed_by)

        update_props = {
            'viewed_by': viewed_by,
            'completed_by_id': params['user'].id,
            'completed_at': datetime.datetime.now()
        }

        nf.__dict__.update(**update_props)
        nf.save()
        return nf
