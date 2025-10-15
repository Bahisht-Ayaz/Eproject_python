from django.shortcuts import render

# Create your views here.
url="https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=[API_KEY]"
url="https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=[API_KEY]"

from django.contrib.sessions.backends import db
from django.shortcuts import render, redirect

def index (request):
    return render(request,"myapp/index.html")

def pricing (request):
    return render(request,"myapp/pricing.html")

def faq (request):
    return render(request,"myapp/faq.html")

def contact (request):
    return render(request,"myapp/contact.html")

def service (request):
    return render(request,"myapp/service.html")

def feedback (request):
    return render(request,"myapp/feedback.html")

def blog_right_sidebar (request):
    return render(request,"myapp/blog-right-sidebar.html")

def coming_soon (request):
    return render(request,"myapp/coming-soon.html")

def blog_left_sidebar (request):
    return render(request,"myapp/blog-left-sidebar.html")

def blog_single(request):
    return render(request, 'myapp/blog_single.html')

def portfolio (request):
    return render(request,"myapp/portfolio.html")

def portfolio_single (request):
    return render(request,"myapp/portfolio-single.html")

def blog_grid (request):
    return render(request,"myapp/blog-grid.html")

def about (request):
    return render(request,"myapp/about.html")

def blog_full_width (request):
    return render(request,"myapp/blog-full-width.html")