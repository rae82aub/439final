from django.db import models
import os, random
from django.conf import settings
from django.core.files import File


GENDER_CHOICES = (
    ("Male", "Male"),
    ("Female", "Female"),
)


class Contact(models.Model):
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="Male")
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

    def save(self, *args, **kwargs):
        # Assign random photo only when creating AND if no photo uploaded
        if not self.pk and not self.profile_photo:

            # Pick gender-specific folder
            if self.gender == "Female":
                img_folder = os.path.join(settings.BASE_DIR, "static", "random_doctors", "female")
            else:
                img_folder = os.path.join(settings.BASE_DIR, "static", "random_doctors", "male")

            # All images in folder
            all_images = os.listdir(img_folder)

            # Already used photos (file names only)
            used = Contact.objects.exclude(profile_photo="").values_list("profile_photo", flat=True)
            used_names = [os.path.basename(u) for u in used]

            # Filter only unused images
            available = [img for img in all_images if img not in used_names]

            # Assign a random unused photo
            if available:
                img_name = random.choice(available)
                img_path = os.path.join(img_folder, img_name)

                with open(img_path, "rb") as f:
                    self.profile_photo.save(img_name, File(f), save=False)

        super().save(*args, **kwargs)



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
   
    pregnancy_safe = models.BooleanField(default=False)
    child_safe = models.BooleanField(default=False)
    minimum_age = models.IntegerField(default=0)
    requires_prescription = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class PharmacyStock(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medicine.name} at {self.pharmacy.name}"
