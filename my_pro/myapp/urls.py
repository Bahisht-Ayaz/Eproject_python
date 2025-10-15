from django.urls import path,include
from . import views

urlpatterns = [
    path ("", views.index, name="index"),
    path('faq.html', views.faq, name='faq'),
    path('feedback.html', views.feedback, name='feedback'),
    path('pricing.html', views.pricing, name='pricing'),
    path('contact.html', views.contact, name='contact'),
    path("about.html", views.about, name="about"),
    path("coming-soon.html", views.coming_soon, name="coming-soon"),
    path("blog-right-sidebar.html", views.blog_right_sidebar, name="blog-right-sidebar"),
    path("blog-left-sidebar.html", views.blog_left_sidebar, name="blog-left-sidebar"),
    path("blog-full-width.html", views.blog_full_width, name="blog-full-width"),
    path("service.html",views.service, name="service"),
    path("portfolio.html",views.portfolio, name="portfolio"),
    path('blog-single.html', views.blog_single, name='blog-single'),
    path("blog-grid.html", views.portfolio, name="blog-grid"),

]