from django.urls import path,include
from . import views

urlpatterns = [
    path ("", views.index, name="index"),
    path('faq.html', views.faq, name='faq'),
    path('feedback.html', views.feedback, name='feedback'),
    path('pricing.html', views.pricing, name='pricing'),
    path('contact.html', views.contact, name='contact'),
    path("about.html", views.about, name="about"),
    path("weatherupdate.html",views.weatherupdate, name="weatherupdate"),
    path("register", views.register, name="reg"),
    path("login", views.login, name="log"),
    path("d", views.dashboard, name="dash"),
    path("logout", views.logout, name="logout")

]