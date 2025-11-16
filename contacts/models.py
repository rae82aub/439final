from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=200)
    speciality = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    hospital = models.CharField(max_length=200)
    experience = models.IntegerField()
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    profile_photo = models.ImageField(upload_to='doctor_photos/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Pharmacy(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    map_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Medicine(models.Model):
    CATEGORY_CHOICES = [
        ('painkiller', 'Painkiller'),
        ('antibiotic', 'Antibiotic'),
        ('allergy', 'Allergy Relief'),
        ('cold_flu', 'Cold & Flu'),
        ('digestive', 'Digestive System'),
        ('vitamin', 'Vitamin / Supplement'),
        ('heart', 'Heart & Blood Pressure'),
        ('skin', 'Skin / Topical'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)

    def __str__(self):
        return self.name


class PharmacyStock(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medicine.name} at {self.pharmacy.name}"
