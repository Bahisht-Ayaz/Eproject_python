from django.shortcuts import render

# Create your views here.

from django.contrib.sessions.backends import db
from django.shortcuts import render, redirect
from django.conf import settings
import requests

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
def register(req):
    if req.method == "POST":
        n = req.POST.get("name")
        e = req.POST.get("email")
        p = req.POST.get("password")

        if not n or not e or not p:
            messages.error(req, "All Fields Are Required")
            return redirect("reg")

        if len(p) < 8:
            messages.error(req, "Password Must Be 8 Characters Long")
            return redirect("reg")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={settings.FIRE}"
        payload = {
        "email" : e,
        "password" : p,
        "requestSecureToken" : True
        }

        response = requests.post(url,payload)

        if response.status_code == 200:
            errorMsg = response.json()
            db.collection("User").add({
                "Name" : n,
                "Email": e,
                "Password": p,
                "Role": "User",
            })
            messages.success(req,"User Registered Successfully")
            return redirect("reg")

    return render(req, "myapp/Register.html")

def login(req):
    if req.method == "POST":
        e = req.POST.get("email")
        p = req.POST.get("password")

        if not e or not p:
            messages.error(req, "All Fields Are Required")
            return redirect("log")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIRE}"
        payload = {
            "email": e,
            "password": p,
            "requestSecureToken": True
        }
        res = requests.post(url,json=payload)

        if res.status_code == 200:
            userInfo = res.json()
            req.session["email"] = userInfo.get("email")
            return redirect("dash")
        else:
            error = res.json().get("error", {}).get("message","Message Not Found")
            print(error)
            if error == "INVALID_LOGIN_CREDENTIALS":
                messages.error(req,"Invalid Credentials Please LogIn again")
            elif error == "INVALID_PASSWORD":
                messages.error(req, "Password Is Incorrect")
            return redirect("log")
    return render(req, "myapp/Login.html")