from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm
from django.core.paginator import Paginator
from .models import Contact, Medicine, Pharmacy, PharmacyStock
import google.generativeai as genai
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Contact, Medicine, FavoriteDoctor, FavoriteMedicine
import random




@login_required
def home(request):
    recent_doctors, recent_medicines = get_recent_items(request)

    health_tips = [
        "Drink at least 6-8 cups of water daily.",
        "Take a 10-minute walk after meals to improve digestion.",
        "Sleep 7-9 hours every night for better brain and heart health.",
        "Wash your hands often - it prevents most infections.",
        "Eat colorful fruits and vegetables for balanced nutrition.",
        "Limit screen time before bed to improve sleep quality.",
        "Schedule annual checkups - prevention matters.",
    ]

    tip_of_the_day = random.choice(health_tips)

    return render(request, "home.html", {
        "recent_doctors": recent_doctors,
        "recent_medicines": recent_medicines,
        "tip_of_the_day": tip_of_the_day,
    })

@login_required
def contact_list(request):
    contacts = Contact.objects.all().order_by("name")

    paginator = Paginator(contacts, 9) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'contacts/contact_list.html', {
        'page_obj': page_obj
    })

@login_required
def contact_add(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_add.html', {'form': form})


@login_required
def contact_update(request, id):
    contact = get_object_or_404(Contact, id=id)
    form = ContactForm(request.POST or None, instance=contact)
    if form.is_valid():
        form.save()
        return redirect('contact_list')
    return render(request, 'contacts/contact_update.html', {'form': form})


@login_required
def contact_delete(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('contact_list')



@login_required
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
@login_required
def contact_detail(request, id):
    doctor = get_object_or_404(Contact, id=id)

    # Recently viewed logic
    viewed = request.session.get("recent_doctors", [])
    if id in viewed:
        viewed.remove(id)
    viewed.insert(0, id)
    request.session["recent_doctors"] = viewed[:6]
    request.session.modified = True

    # ✅ Check if already favorited
    is_fav = FavoriteDoctor.objects.filter(user=request.user, doctor=doctor).exists()

    return render(request, 'contacts/contact_detail.html', {
        'doctor': doctor,
        'is_fav': is_fav,   # ✅ passing to template
    })


@login_required
def find_medicine(request):
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")

    # NEW FILTERS
    pregnancy_safe = request.GET.get("pregnancy_safe")
    child_safe = request.GET.get("child_safe")
    otc = request.GET.get("otc")  # over-the-counter only

    medicines = Medicine.objects.all()

    # TEXT SEARCH
    if query:
        medicines = medicines.filter(name__icontains=query)

    # CATEGORY FILTER
    if category and category.lower() != "all":
        medicines = medicines.filter(category__iexact=category)

    # SAFETY FILTERS
    if pregnancy_safe == "on":
        medicines = medicines.filter(pregnancy_safe=True)

    if child_safe == "on":
        medicines = medicines.filter(child_safe=True)

    if otc == "on":
        medicines = medicines.filter(requires_prescription=False)

    return render(request, "contacts/find_medicine.html", {
        "results": medicines,
        "query": query,
        "selected_category": category,
    })

@login_required
def medicine_detail(request, id):
    medicine = get_object_or_404(Medicine, id=id)
    stock_entries = PharmacyStock.objects.filter(medicine=medicine)

    is_fav = FavoriteMedicine.objects.filter(user=request.user, medicine=medicine).exists()

    return render(request, "contacts/medicine_detail.html", {
        "medicine": medicine,
        "stock_entries": stock_entries,
        "is_fav": is_fav,
    })

def get_recent_items(request):
    recent_doctor_ids = request.session.get("recent_doctors", [])
    recent_medicine_ids = request.session.get("recent_medicines", [])

    recent_doctors = Contact.objects.filter(id__in=recent_doctor_ids)
    recent_medicines = Medicine.objects.filter(id__in=recent_medicine_ids)

    return recent_doctors, recent_medicines


@login_required
def extract_medicine_names(text):
    return re.findall(r"[A-Z][a-zA-Z0-9+-]{2,}", text)

@login_required
def assistant(request):
    message = ""
    short_points = []
    meds_points = []
    doctor_points = []
    available_medicines = []

    if request.method == "POST":
        message = request.POST.get("message", "")

        prompt = f"""
        IMPORTANT: Use this exact format:

        1. Short explanation: <one or two sentences>

        2. Recommended OTC medicines:
        - item
        - item
        - item

        3. When to see a doctor:
        - item
        - item
        - item

        Symptoms: {message}
        """

        genai.configure(api_key="AIzaSyDybJxbjtGEbYSh7QTf9yvY0laSRY9bPNw")
        model = genai.GenerativeModel("models/gemini-2.0-flash")

        ai = model.generate_content(prompt)
        response = ai.text

        try:
            part1 = response.split("2.")[0]
            part2to3 = response.split("2.")[1]

            part2 = part2to3.split("3.")[0]
            part3 = part2to3.split("3.")[1]
        except:
            part1, part2, part3 = "", "", ""

        short_clean = (
            part1.replace("1. Short explanation:", "")
            .replace("1. Short explanation", "")
            .strip()
        )

        meds_clean = (
            part2.replace("Recommended OTC medicines:", "")
            .replace("2. Recommended OTC medicines:", "")
            .strip()
        )

        doctor_clean = (
            part3.replace("When to see a doctor:", "")
            .replace("3. When to see a doctor:", "")
            .strip()
        )

        short_points = [p.strip() for p in short_clean.split("-") if p.strip()]
        meds_points = [p.strip() for p in meds_clean.split("-") if p.strip()]
        doctor_points = [p.strip() for p in doctor_clean.split("-") if p.strip()]

    return render(request, "contacts/assistant.html", {
        "short_points": short_points,
        "meds_points": meds_points,
        "doctor_points": doctor_points,
        "message": message,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")



def signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect("home")

    return render(request, "signup.html")


def health_tips(request):
    return render(request, "contacts/health_tips.html")


@login_required
def toggle_favorite_doctor(request, doctor_id):
    doctor = get_object_or_404(Contact, id=doctor_id)

    fav, created = FavoriteDoctor.objects.get_or_create(
        user=request.user,
        doctor=doctor
    )

    if not created:
        fav.delete()

    return redirect('contact_detail', doctor_id)


@login_required
def toggle_favorite_medicine(request, med_id):
    medicine = get_object_or_404(Medicine, id=med_id)

    fav, created = FavoriteMedicine.objects.get_or_create(
        user=request.user,
        medicine=medicine
    )

    if not created:
        fav.delete()

    return redirect('medicine_detail', med_id)

@login_required
def favorites_list(request):
    fav_doctors = FavoriteDoctor.objects.filter(user=request.user)
    fav_medicines = FavoriteMedicine.objects.filter(user=request.user)

    return render(request, 'contacts/favorites.html', {
        'fav_doctors': fav_doctors,
        'fav_medicines': fav_medicines,
    })

def logout_view(request):
    logout(request)
    return redirect("login")
