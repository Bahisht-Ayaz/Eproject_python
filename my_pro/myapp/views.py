
# Create your views here.
from django.contrib import messages
from my_pro.firebase_config import db
from firebase_admin import firestore
from django.shortcuts import render, redirect
from django.conf import settings
import requests

def index (request):
    return render(request,"myapp/index.html")

def pricing (request):
    return render(request,"myapp/pricing.html")

def faq (request):
    return render(request,"myapp/faq.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("user_name")
        email = request.POST.get("user_email")
        subject = request.POST.get("user_subject")
        message = request.POST.get("user_message")

        if not name or not email or not subject or not message:
            messages.error(request, "⚠️ Please fill in all fields.")
            return redirect("contact")

        try:
            # Send to Firestore
            db.collection("contactMessages").add({
                "name": name,
                "email": email,
                "subject": subject,
                "message": message,
                "timestamp": firestore.SERVER_TIMESTAMP,
            })
            messages.success(request, "✅ Message sent successfully!")
        except Exception as e:
            print("Firestore error:", e)
            messages.error(request, "❌ Failed to send message. Please try again.")

        return redirect("contact")

    return render(request, "myapp/contact.html")

def weatherupdate (request):
    return render(request,"myapp/weatherupdate.html")


def feedback(request):
    if request.method == "POST":
        name = request.POST.get("user_name")
        email = request.POST.get("user_email")
        rate = request.POST.get("Rate_us")
        message = request.POST.get("user_message")

        if not name or not email or not rate or not message:
            messages.error(request, "⚠️ Please fill in all fields.")
            return redirect("feedback")

        try:
            # ✅ Save feedback to Firestore
            db.collection("Feedbacks").add({
                "name": name,
                "email": email,
                "rating": rate,
                "message": message,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            messages.success(request, "✅ Thank you for your feedback!")
        except Exception as e:
            print("Firestore error:", e)
            messages.error(request, "❌ Something went wrong. Try again later.")

        return redirect("feedback")

    return render(request, "myapp/feedback.html")



def about (request):
    return render(request,"myapp/about.html")

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

    return render(req, "myapp/register.html")

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
    return render(req, "myapp/login.html")

def dashboard(req):
    if "email" not in req.session:
        return redirect('log')  # Agar login nahi to login page pe bhej do
    uemail = req.session["email"]
    return render(req, "myapp/index.html", {"e": uemail})


def logout(request):
    try:
        del request.session['email']
    except KeyError:
        pass
    return redirect('log')  # Login page pe redirect karein


def Admin_dash (request):
    return render(request,"myapp/Admin.html")


def user_list (request):
    return render(request,"myapp/user_list.html")


def feedback_details(request):
    try:
        feedback_ref = db.collection("Feedbacks").order_by("timestamp", direction=firestore.Query.DESCENDING)
        feedback_docs = feedback_ref.stream()
        feedback_list = []

        for doc in feedback_docs:
            data = doc.to_dict()
            feedback_list.append({
                "name": data.get("name"),
                "email": data.get("email"),
                "rating": data.get("rating"),
                "message": data.get("message"),
                "timestamp": data.get("timestamp")
            })
    except Exception as e:
        print("Error fetching feedbacks:", e)
        feedback_list = []

    return render(request, "myapp/feedback_details.html", {"feedbacks": feedback_list})
