if __name__ == "__main__":

    from pathlib import Path
    import sys

    project_dir = str(Path().resolve().parents[1])
    sys.path.append('%s/' % project_dir)

    import django
    from redington import settings

    DJANGO_SETTINGS_MODULE = settings
    django.setup()

    from users.models import RedUser, PasswordResetTokens
    import datetime
    from rest_framework_jwt.settings import api_settings
    from common.mails.BaseMails import BaseMails
    from django.db.models import Q

    partners = RedUser.objects.filter(profile__user_type='P') \
        .exclude(Q(email='') | Q(email=None) | Q(
        pk__in=[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 1474, 18, 19, 20, 21, 22, 23, 24, 25, 26, 1475, 28, 27,
                29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42
                ]))

    for partner in partners:
        user = partner
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
                'reset_link': '%s?tk=%s' % ('https://portal.redingtoncloud.com/auth/password/reset/confirm', token)
            }
        )

        print('Sent to : ', user.username)
