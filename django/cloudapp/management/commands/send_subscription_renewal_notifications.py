from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):

    help = "This command will send notifications to partner and business team about subscription renewal"

    def handle(self, *args, **options):
        print('Subscription renewal alert!')
        from cloudapp.management.commands.subscriptions_renewal_notifications import SubscriptionsRenewalNotifications

        try:
            subscription = SubscriptionsRenewalNotifications()
            subscription.perform_actions()
            subscription.check_subscriptions()
        except Exception:
            raise CommandError('Sending subscriptions renewal alert failed!')

