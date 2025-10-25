from django.urls import path,include
from . import views

urlpatterns = [
    path ("", views.index, name="index"),
    path('faq', views.faq, name='faq'),
    path('feedback', views.feedback, name='feedback'),
    path('pricing', views.pricing, name='pricing'),
    path('contact', views.contact, name='contact'),
    path("about", views.about, name="about"),
    path("weatherupdate",views.weatherupdate, name="weatherupdate"),
    path("register", views.register, name="reg"),
    path("login", views.login, name="log"),
    path("d", views.dashboard, name="dash"),
    path("logout", views.logout, name="logout"),
    path("Admin_dash", views.Admin_dash, name="Admin_dash"),
    path("user_list", views.user_list, name="user_list"),
    path("feedback_details", views.feedback_details, name="feedback_details"),
    path('predict', views.predict_weather, name='predict_weather'),

]