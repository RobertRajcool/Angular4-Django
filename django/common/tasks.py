from redington_uber.celery import app
from celery import shared_task


@shared_task(name='send_emails_and_notifications')
def send_emails_and_notifications(*args, **kwargs):
    """ Sending emails & notifications """

    from common.receivers import send_mail_notifications

    required_arguments = ['sender', 'trigger', 'details']

    for argument in required_arguments:
        if argument not in kwargs:
            raise AttributeError('Argument not found :', argument)

    try:
        response = send_mail_notifications.send(sender=kwargs['sender'],
                                                trigger=kwargs['trigger'],
                                                details=kwargs['details'])

        return True
    except Exception as e:
        print(e)
        return False
