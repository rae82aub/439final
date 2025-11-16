from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

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
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("signup/", views.signup, name="signup"),

]
