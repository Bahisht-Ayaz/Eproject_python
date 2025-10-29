from django.urls import path,include
from . import views

urlpatterns = [
    path ("", views.index, name="index"),
    path('faq', views.faq, name='faq'),
    path('feedback', views.feedback, name='feedback'),
    path('webscrapping', views.project_price_with_weather, name='webscrapping'),
    path('contact', views.contact, name='contact'),
    path("about", views.about, name="about"),
    path("weatherupdate",views.weatherupdate, name="weatherupdate"),
    path("register", views.register, name="reg"),
    path("login", views.login, name="log"),
    path("", views.dashboard, name="dash"),
    path("logout", views.logout, name="logout"),
    path("user_list", views.user_list, name="user_list"),
    path("feedback_details", views.feedback_details, name="feedback_details"),
    path('predict', views.predict_weather, name='predict_weather'),
    path("admin_login/", views.admin_login, name="admin_login"),
    path("admin_dashboard/", views.admin_dashboard, name="Admin"),
    path("admin_logout/", views.admin_logout, name="admin_logout"), # ✅ important

]