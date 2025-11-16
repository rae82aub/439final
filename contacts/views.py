from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm
from django.core.paginator import Paginator
from .models import Contact, Medicine, Pharmacy, PharmacyStock
import google.generativeai as genai
from django.shortcuts import render
import re

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




def extract_medicine_names(text):
    # Finds capitalized words (Panadol, Brufen, Gaviscon)
    return re.findall(r"[A-Z][a-zA-Z0-9+-]{2,}", text)



def assistant(request):
    response_text = ""
    short_expl = ""
    meds = ""
    doctor = ""
    message = ""
    available_medicines = []

    if request.method == "POST":
        message = request.POST.get("message", "")

        prompt = f"""
        dont use * replace it with - for lists
        Give a medical summary in EXACTLY this format:

        1. Short explanation: <one sentence>
        2. Recommended OTC medicines:<list with dashes> Recommend specific over-the-counter medicines available in Lebanon,
           include BRAND NAMES like Panadol, Brufen, Buscopan, Gaviscon, Strepsils, Telfast, Claritin, Otrivin, Efferalgan, Imodium.
        3. When to see a doctor: <list with dashes>

        Use REAL line breaks.
        Symptoms: {message}
        """

        genai.configure(api_key="AIzaSyDybJxbjtGEbYSh7QTf9yvY0laSRY9bPNw")
        model = genai.GenerativeModel("models/gemini-2.0-flash")

        try:
            ai = model.generate_content(prompt)
            response_text = ai.text

            # ---- SPLIT INTO 3 PARTS ----
            parts = response_text.split("2. Recommended")
            part1 = parts[0] if len(parts) > 0 else ""
            rest = "2. Recommended" + parts[1] if len(parts) > 1 else ""

            parts2 = rest.split("3. When")
            part2 = parts2[0] if len(parts2) > 0 else ""
            part3 = "3. When" + parts2[1] if len(parts2) > 1 else ""

            short_expl = part1.replace("1. Short explanation:", "").strip()
            meds = part2.replace("2. Recommended OTC medicines:", "").strip()
            doctor = part3.replace("3. When to see a doctor:", "").strip()

            # ---- EXTRACT MEDICINE NAMES FROM AI RESPONSE ----
            medicine_names = extract_medicine_names(response_text)

            if medicine_names:
                # Match ANY medicine name found
                regex = "|".join(medicine_names)
                available_medicines = Medicine.objects.filter(
                    name__iregex=regex
                )

        except Exception as e:
            response_text = f"Error: {e}"

    return render(request, "contacts/assistant.html", {
        "short": short_expl,
        "meds": meds,
        "doctor": doctor,
        "message": message,
        "available_medicines": available_medicines,
    })