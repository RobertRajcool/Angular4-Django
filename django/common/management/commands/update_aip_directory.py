from django.core.management import BaseCommand
from common.models import AipDirectory
import pandas
import os


class Command(BaseCommand):
    help = "Command to update the AIP directory table records"

    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', type=str, nargs='?',
                            default=None, help="Path of pincodes directory file (.csv)")
        parser.add_argument('-bs', '--batch-size', type=int, nargs='?',
                            default=50, help="Path of pincodes directory file (.csv)")

    def handle(self, *args, **options):
        file_path = options.get('file', None)
        batch_size = options.get('batch_size', 50)

        if not file_path:
            raise ValueError('File Not Provided')

        if not os.path.exists(file_path):
            raise FileNotFoundError("File Not Found")

        if not os.path.splitext(file_path)[1] == '.csv':
            raise ValueError("Invalid File : Provide a valid CSV file")

        DF = pandas.read_csv(file_path,
                             header=0,
                             encoding="ISO-8859-1")

        p_list = DF.to_dict(orient='records')

        def import_to_db(records):
            AipDirectory.objects.bulk_create(records, batch_size=batch_size)

        batch = list()
        i = 1
        for record in p_list:
            batch.append(AipDirectory(**{
                "office_name": record['officename'],
                "pincode": record['pincode'],
                "office_type": record['officetype'],
                "delivery_status": record['Deliverystatus'],
                "division": record['divisionname'],
                "region": record['regionname'],
                "circle": record['circlename'],
                "taluk": record['taluk'],
                "district": record['districtname'],
                "state": record['statename'],
            }))
            i += 1

            if i == batch_size:
                import_to_db(batch)
                batch = list()
                i = 1

        if len(batch) > 0:
            import_to_db(batch)
            batch = list()
            i = 1

        return "Imported successfully"
