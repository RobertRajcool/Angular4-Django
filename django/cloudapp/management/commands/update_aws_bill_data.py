from django.core.management import BaseCommand

from background_scripts.aws.aws_biller import AWSBiller


class Command(BaseCommand):
    help = 'This command will checks aws bill updates in s3, dowloads and loads into elasticsearch'

    def handle(self, *args, **options):
        biller = AWSBiller()
        print("Checking for updates", ('.' * 40))
        response = biller.fetch_s3bills()

        if len(response) > 0:
            print("Loading bill data into elasticsearch", ('.' * 24))
            biller.load_to_elasticsearch()
        else:
            print("No updates available")
