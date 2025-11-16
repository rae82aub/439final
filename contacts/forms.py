from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'speciality', 'city', 'hospital',
                  'experience', 'fees', 'rating', 'profile_photo', 'phone']
