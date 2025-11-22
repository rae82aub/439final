from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import toggle_favorite_doctor
from .views import toggle_favorite_medicine
urlpatterns = [
    # HOME
    path("", views.home, name="home"),

    # CONTACTS (protected by @login_required in the views)
    path("list/", views.contact_list, name="contact_list"),
    path("add/", views.contact_add, name="contact_add"),
    path("update/<int:id>/", views.contact_update, name="contact_update"),
    path("delete/<int:id>/", views.contact_delete, name="contact_delete"),
    path("doctor/<int:id>/", views.contact_detail, name="contact_detail"),
    path("recommend/", views.recommend, name="recommend"),

    # MEDICINES
    path("find_medicine/", views.find_medicine, name="find_medicine"),
    path("medicine/<int:id>/", views.medicine_detail, name="medicine_detail"),

    # ASSISTANT
    path("assistant/", views.assistant, name="assistant"),

    # AUTH

    path("signup/", views.signup, name="signup"),
    path("health-tips/", views.health_tips, name="health_tips"),
    path('favorite-doctor/<int:doctor_id>/', views.toggle_favorite_doctor, name='toggle_favorite_doctor'),
    path('favorite-medicine/<int:med_id>/', views.toggle_favorite_medicine, name='toggle_favorite_medicine'),
    path('favorites/', views.favorites_list, name='favorites_list'),

]
