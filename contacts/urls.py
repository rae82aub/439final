from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("list/", views.contact_list, name="contact_list"),
    path("add/", views.contact_add, name="contact_add"),
    path("update/<int:id>/", views.contact_update, name="contact_update"),
    path("delete/<int:id>/", views.contact_delete, name="contact_delete"),
    path("doctor/<int:id>/", views.contact_detail, name="contact_detail"),
    path("recommend/", views.recommend, name="recommend"),

    path("find_medicine/", views.find_medicine, name="find_medicine"),
    path("medicine/<int:id>/", views.medicine_detail, name="medicine_detail"),

    path("assistant/", views.assistant, name="assistant"),
     

]
