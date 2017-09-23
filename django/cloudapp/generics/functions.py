from common.models import PartnerFeedback
from common.mails.BaseMails import BaseMails
from django.conf import settings
from cloudapp.generics.constant import AppContants


def generate_order_number():
    """ Generates new order number """

    #last_order_instance = Orders.objects.last()
    #order_number = 'ORD%06d' % (last_order_instance.id + 1) if last_order_instance is not None else 'ORD%06d' % 16000

    return True


def generate_feedback_number():
    """ Generates new feedback number """

    last_feedback_instance = PartnerFeedback.objects.last()
    feedback_number = 'S%04d' % (last_feedback_instance.id + 1) if last_feedback_instance is not None else 'S%04d' % 1

    return feedback_number


def generate_pi_number():
    """ Generates new feedback number """

    #last_pi_instance = ProformaInvoices.objects.last()
    #pi_number = 'PI%08d' % (last_pi_instance.id + 1) if last_pi_instance is not None else 'PI%08d' % 1

    return True


def generate_web_so_number():
    """ Generates new web order number """

    #last_order_instance = WebSalesOrders.objects.last()
    #web_order_number = 'C%06d' % (last_order_instance.id + 1) if last_order_instance is not None else 'C%06d' % 10950

    return True


def currencyFormat(value, currencyFormat):
    import locale
    try:
        if currencyFormat == 1:
            locale.setlocale(locale.LC_ALL, 'en_IN')
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    loc = locale.localeconv()
    return locale.currency(float(value), loc['currency_symbol'], grouping=True)


def get_traceback(self, exc_info=None):
    """Helper function to return the traceback as a string"""
    import traceback
    import sys
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))


def send_task_status_email(subject='Celery Task Status', title='Celery Task Status ', message='No Message Received'):
    """ Sends a email to Technical Team regarding celery task status"""
    BaseMails.send_mail(subject=subject,
                        recipients=settings.TECH_TEAM,
                        template_name='plain.html',
                        template_data={
                            'Title': title,
                            'message': message,
                            'domain_name': AppContants.DOMAIN_NAME
                        }
                        )
