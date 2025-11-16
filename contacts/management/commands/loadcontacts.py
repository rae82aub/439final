import csv
from django.core.management.base import BaseCommand
from contacts.models import Contact

class Command(BaseCommand):
    help = "Load contacts from CSV"

    def handle(self, *args, **kwargs):
        with open('contacts/data/Doctors.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            Contact.objects.all().delete()

            for row in reader:
                Contact.objects.create(
                    name=row['name'],
                    speciality=row['speciality'],
                    city=row['city'],
                    hospital=row['hospital'],
                    experience=row['experience'],
                    fees=row['fees'],
                    rating=row['rating'],
                )

        self.stdout.write(self.style.SUCCESS("Contacts imported successfully"))
