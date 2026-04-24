from django.core.management.base import BaseCommand
from members.models import State, District, Mandal, Village
import pandas as pd
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the database with location data from Excel files (States, Districts, Mandals, Villages).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing location data before importing',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing location data...'))
            Village.objects.all().delete()
            Mandal.objects.all().delete()
            District.objects.all().delete()
            State.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing location data cleared.'))

        self.stdout.write(self.style.SUCCESS('Starting population of location data from Excel files...'))

        # Excel files to process
        excel_files = [
            'Andhrapradesh.xls',
            'Tamilnadu.xls', 
            'Kerala.xls',
            'Karnataka.xls'
        ]

        for excel_file in excel_files:
            file_path = os.path.join(settings.BASE_DIR, excel_file)
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'Excel file not found: {file_path}'))
                continue

            self.stdout.write(self.style.SUCCESS(f'Processing {excel_file}...'))
            
            try:
                # Read Excel file
                df = pd.read_excel(file_path)
                
                # Check if required columns exist and handle variations
                required_columns = ['State', 'District', 'Mandal', 'Village']
                column_mapping = {
                    'Mnadal': 'Mandal',  # Handle typo in Karnataka.xls
                    'Mandal': 'Mandal',
                    'District': 'District',
                    'State': 'State',
                    'Village': 'Village'
                }
                
                # Rename columns if needed
                df_columns = df.columns.tolist()
                for old_col, new_col in column_mapping.items():
                    if old_col in df_columns and new_col not in df_columns:
                        df = df.rename(columns={old_col: new_col})
                
                if not all(col in df.columns for col in required_columns):
                    self.stdout.write(self.style.ERROR(f'Required columns not found in {excel_file}. Expected: {required_columns}, Found: {df.columns.tolist()}'))
                    continue

                # Process each row
                for index, row in df.iterrows():
                    state_name = str(row['State']).strip()
                    district_name = str(row['District']).strip()
                    mandal_name = str(row['Mandal']).strip()
                    village_name = str(row['Village']).strip()

                    # Skip empty rows
                    if not all([state_name, district_name, mandal_name, village_name]) or state_name == 'nan':
                        continue

                    # Create or get State
                    state, created = State.objects.get_or_create(name=state_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created State: {state_name}'))

                    # Create or get District
                    district, created = District.objects.get_or_create(state=state, name=district_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created District: {district_name} in {state_name}'))

                    # Create or get Mandal
                    mandal, created = Mandal.objects.get_or_create(district=district, name=mandal_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created Mandal: {mandal_name} in {district_name}'))

                    # Create or get Village
                    village, created = Village.objects.get_or_create(mandal=mandal, name=village_name)
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created Village: {village_name} in {mandal_name}'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {excel_file}: {str(e)}'))
                continue

        # Display summary
        state_count = State.objects.count()
        district_count = District.objects.count()
        mandal_count = Mandal.objects.count()
        village_count = Village.objects.count()

        self.stdout.write(self.style.SUCCESS('Location data population complete.'))
        self.stdout.write(self.style.SUCCESS(f'Summary: {state_count} States, {district_count} Districts, {mandal_count} Mandals, {village_count} Villages'))
