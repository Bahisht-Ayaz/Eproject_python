
# Create your views here.
from django.contrib import messages
from my_pro.firebase_config import db
from firebase_admin import firestore
from django.shortcuts import render, redirect
from django.conf import settings
import requests
import joblib
import pandas as pd
import os

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


def user_list(request):
    try:
        user_ref = db.collection("User").order_by("timestamp", direction=firestore.Query.DESCENDING)
        user_docs = user_ref.stream()
        user_list = []

        for doc in user_docs:
            data = doc.to_dict()
            user_list.append({
                "Name": data.get("Name"),
                "Email": data.get("Email"),
                "Role": data.get("Role"),
            })
    except Exception as e:
        print("Error fetching feedbacks:", e)
        feedback_list = []

    return render(request, "myapp/feedback_details.html", {"User": user_list})


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





# Model load
model_path = os.path.join(os.path.dirname(__file__), "models", "best_pipeline.joblib")
model = joblib.load(model_path)

def predict_weather(request):
    result = None
    probability = None

    if request.method == "POST":
        city = request.POST.get("city")
        year = int(request.POST.get("year"))
        avg_temp = float(request.POST.get("avg_temp"))
        rainfall_mm = float(request.POST.get("rainfall_mm"))
        humidity = float(request.POST.get("humidity"))

        # DataFrame for prediction
        df = pd.DataFrame([{
            "city": city,
            "year_rel": year - 2015,
            "avg_temp": avg_temp,
            "rainfall_mm": rainfall_mm,
            "humidity": humidity
        }])

        # Prediction
        proba = model.predict_proba(df)[:, 1][0]
        pred = model.predict(df)[0]

        if proba >= 0.5:
            result = "Baarish hogi ☔"
        else:
            result = "Baarish nahi hogi ☀️"

        probability = round(proba * 100, 2)

    return render(request,"myapp/predict_weather.html", {
        "result": result,
        "probability": probability
    })