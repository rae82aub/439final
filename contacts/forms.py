from django import forms
from .models import Contact
from .models import AppointmentRequest

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            "name", "gender", "speciality",
            "city", "hospital", "experience",
            "fees", "rating", "profile_photo", "phone"
        ]

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ['full_name', 'phone', 'email', 'preferred_date', 'preferred_time', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+961 71 234 567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_time': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe symptoms or preferred time...'}),
        }
