from rest_framework.views import exception_handler
from rest_framework.response import Response
from common.custom_exceptions import RedValidationErr


def redington_exception_handler(exc, context):
    response = exception_handler(exc, context)

    """ Skipping Custom Validation Errors """
    if isinstance(exc, RedValidationErr):
        data = {
            'status_code': response.status_code,
            'status_text': response.status_text,
            'detail': None
        }
        if isinstance(exc.detail, list):
            data['detail'] = ', '.join(exc.detail)
        else:
            data['detail'] = exc.detail
        response.data = data
        return response

    requested_url = context['request'].get_full_path()
    requested_user = context['request'].user.username
    # Now add the HTTP status code to the response.
    import uuid
    uuid = uuid.uuid4()
    print(exc)
    file = open('/tmp/errors.log', 'a')
    file.write("----- Start %s \n" %(uuid,))
    file.write("Requested URL: %s \n" %(requested_url,))
    file.write("Requested User: %s \n" % (requested_user,))
    file.write(_get_traceback(exc))
    file.write("----- End %s \n" %(uuid,))
    file.close()

    message = "There was an error processing this request. The administrator has been informed. Error ID: %s" %(uuid,)
    if response is not None:
        response.data['detail'] = message
        #response.data['status_code'] = response.status_code
    #if unhandled Exceptions
    elif response is None:
        data={'detail': message}

        return Response(data,status=500)
    return response


def _get_traceback(self, exc_info=None):
    """Helper function to return the traceback as a string"""
    import traceback
    import sys
    return '\n'.join(traceback.format_exception(*(exc_info or sys.exc_info())))