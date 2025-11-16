from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm
from django.core.paginator import Paginator
from .models import Contact, Medicine, Pharmacy, PharmacyStock

def home(request):
    return render(request, 'contacts/home.html')

def contact_list(request):
    contacts = Contact.objects.all().order_by("name")

    paginator = Paginator(contacts, 9) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'contacts/contact_list.html', {
        'page_obj': page_obj
    })


def contact_add(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_add.html', {'form': form})

def contact_update(request, id):
    contact = get_object_or_404(Contact, id=id)
    form = ContactForm(request.POST or None, instance=contact)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_update.html', {'form': form})

def contact_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('contact_list')

def recommend(request):
    specialties = Contact.objects.values_list('speciality', flat=True).distinct()
    cities = Contact.objects.values_list('city', flat=True).distinct()

    speciality = request.GET.get('speciality')
    city = request.GET.get('city')
    max_fee = request.GET.get('max_fee')

    results = Contact.objects.all()

    if speciality and speciality != "":
        results = results.filter(speciality=speciality)

    if city and city != "":
        results = results.filter(city=city)

    if max_fee and max_fee != "":
        results = results.filter(fees__lte=max_fee)

    return render(request, 'contacts/recommend.html', {
        'specialties': specialties,
        'cities': cities,
        'results': results,
    })
    
def contact_detail(request, id):
    doctor = get_object_or_404(Contact, id=id)
    return render(request, 'contacts/contact_detail.html', {'doctor': doctor})

def find_medicine(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")

    medicines = Medicine.objects.all()

    if query:
        medicines = medicines.filter(name__icontains=query)

    if category and category.lower() != "all":
        medicines = medicines.filter(category__iexact=category)

    return render(request, "contacts/find_medicine.html", {
        "results": medicines,
        "query": query,
        "selected_category": category
    })

def medicine_detail(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    stock_entries = PharmacyStock.objects.filter(medicine=medicine)

    return render(request, "contacts/medicine_detail.html", {
        "medicine": medicine,
        "stock_entries": stock_entries
    })
def assistant(request):
    message = ""
    response = ""
    medicines = []

    SYMPTOM_MAP = {
        "headache": ["Panadol", "Advil", "Acamol"],
        "fever": ["Panadol", "Panadol Extra"],
        "flu": ["Panadol Cold & Flu", "Actifed", "Otrivin"],
        "cold": ["Actifed", "Otrivin", "Panadol Cold & Flu"],
        "allergy": ["Claritin", "Zyrtec"],
        "heartburn": ["Gaviscon", "Nexium", "Buscopan"],
        "acidity": ["Gaviscon", "Nexium", "Buscopan"],
        "stomach pain": ["Buscopan"],
        "infection": ["Augmentin", "Cipro", "Zithromax"],
        "antibiotic": ["Augmentin", "Cipro", "Zithromax"],
        "skin rash": ["Bepanthen", "Betadine"],
        "rash": ["Bepanthen", "Betadine"],
    }

    if request.method == "POST":
        message = request.POST.get("message", "").lower()

        matched = None
        for symptom, meds in SYMPTOM_MAP.items():
            if symptom in message:
                matched = meds
                break

        if matched:
            response = "These medicines may help based on your symptoms:"
            medicines = Medicine.objects.filter(name__in=matched)
        else:
            response = "No matching symptoms found. Try describing your issue differently."

    return render(request, "contacts/assistant.html", {
        "message": message,
        "response": response,
        "medicines": medicines
    })
