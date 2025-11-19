from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Contact, Medicine, Pharmacy, PharmacyStock

@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    list_display = ('name', 'speciality', 'city', 'hospital', 'fees', 'rating')
    search_fields = ('name', 'speciality', 'city', 'hospital')
    list_filter = ('city', 'speciality', 'hospital')



@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price',
        'pregnancy_safe', 'child_safe', 'minimum_age', 'requires_prescription'
    )
    list_filter = (
        'category', 'pregnancy_safe', 'child_safe', 'requires_prescription'
    )

@admin.register(Pharmacy)
class PharmacyAdmin(ImportExportModelAdmin):
    list_display = ('name', 'city', 'address', 'phone', 'map_link')
    search_fields = ('name', 'city')


@admin.register(PharmacyStock)
class PharmacyStockAdmin(ImportExportModelAdmin):
    list_display = ('medicine', 'pharmacy', 'price', 'in_stock')
    list_filter = ('pharmacy', 'medicine', 'in_stock')
    search_fields = ('medicine__name', 'pharmacy__name')

