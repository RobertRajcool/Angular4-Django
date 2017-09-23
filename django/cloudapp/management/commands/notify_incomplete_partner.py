from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    """
    This is the child Command class of BaseCommand class
    Through this class only we can pass the commands for execution via manage.py
    Execution : python manage.py notify_incomplete_partner
    """
    def handle(self, *args, **options):
        """
        This is the base function of this child Command class
        Through which class only all the actions to be performed
        :param args:
        :param options:
        :return:
        """
        print('Sending incomplete registration partner notifications!')
        try:
            from background_scripts.partner.partner_registration_incomplete import PartnerRegistrationIncomplete
            notify_to_incomplete_partner = PartnerRegistrationIncomplete()
            notify_to_incomplete_partner.perform_actions()
        except Exception:
            raise CommandError('Sending incomplete registration partner notifications failed!')


