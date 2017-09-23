from django.dispatch import Signal

send_mail_notifications = Signal(providing_args=['trigger', 'details'])


