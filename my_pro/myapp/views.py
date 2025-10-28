
# Create your views here.
import firebase_admin
from django.contrib import messages
from my_pro.firebase_config import db
from firebase_admin import firestore, auth
from django.shortcuts import render, redirect
from django.conf import settings
import requests
import joblib
import pandas as pd
import os

def index (request):
    return render(request,"myapp/index.html")


def faq (request):
    return render(request,"myapp/faq.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("user_name")
        email = request.POST.get("user_email")
        phone = request.POST.get("user_number")
        message = request.POST.get("user_message")

        if not name or not email or not phone or not message:
            messages.error(request, "⚠️ Please fill in all fields.")
            return redirect("contact")

        try:
            # Send to Firestore
            db.collection("contactMessages").add({
                "name": name,
                "email": email,
                "phone_no": phone,
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
                "timestmape":firestore.SERVER_TIMESTAMP
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
        # Firestore collection reference (timestamp optional)
        user_ref = db.collection("User")

        # Agar timestamp field exist nahi karti to ye safe version use karein:
        try:
            user_docs = user_ref.order_by("timestmape", direction=firestore.Query.DESCENDING).stream()
        except Exception:
            user_docs = user_ref.stream()

        user_list = []
        for doc in user_docs:
            data = doc.to_dict()
            user_list.append({
                "id": doc.id,  # ✅ User ID include kar diya
                "Name": data.get("Name", "N/A"),  # ✅ lowercase keys (template ke liye match)
                "Email": data.get("Email", "N/A"),
                "Role": data.get("Role", "N/A"),
            })

        print(f"✅ {len(user_list)} users fetched from Firestore")

    except Exception as e:
        print("❌ Error fetching users:", e)
        user_list = []

    # ✅ Correct context name
    return render(request, "myapp/user_list.html", {"users": user_list})

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


def webscrapping (request):
    return render(request,"myapp/webscrapping.html")

import requests
from bs4 import BeautifulSoup
import feedparser
from django.shortcuts import render
from django.utils import timezone

# ---------- Config ----------
OWM_API_KEY = "30f32fd8eb1ec1c3f7a1efad953498c1"
DEFAULT_CITY = "Karachi"

# Replace these with real RSS feeds if needed
WEATHER_NEWS_FEEDS = [
    "https://www.weather.gov/rss_page.php?site_name=nws"
]

# ---------- OpenWeatherMap API ----------
def fetch_forecast_via_api(city=DEFAULT_CITY, api_key=OWM_API_KEY):
    if not api_key:
        return None
    try:
        # Current weather
        res = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": OWM_API_KEY, "units": "metric"}
        )
        res.raise_for_status()
        current = res.json()

        # 5-day forecast
        f_res = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={"q": city, "appid": api_key, "units": "metric"}, timeout=8
        )
        f_res.raise_for_status()
        forecast = f_res.json()

        # Simplify forecast to daily summary
        daily = {}
        for item in forecast.get("list", []):
            dt_txt = item.get("dt_txt")
            date_key = dt_txt.split(" ")[0]
            temps = daily.setdefault(date_key, {"temps": [], "conditions": []})
            temps["temps"].append(item["main"]["temp"])
            temps["conditions"].append(item["weather"][0]["description"])

        daily_summary = []
        for date_key, info in daily.items():
            daily_summary.append({
                "date": date_key,
                "temp_min": min(info["temps"]),
                "temp_max": max(info["temps"]),
                "condition": max(set(info["conditions"]), key=info["conditions"].count)
            })

        return {
            "source": "openweathermap",
            "city": current.get("name", city),
            "current": {
                "temp": current["main"]["temp"],
                "description": current["weather"][0]["description"],
                "humidity": current["main"]["humidity"],
                "wind": current["wind"]["speed"]
            },
            "daily": daily_summary[:5]  # first 5 days
        }

    except Exception as e:
        print("API fetch failed:", e)
        return None


# ---------- Dummy fallback (if API fails) ----------
def fetch_forecast_fallback(city=DEFAULT_CITY):
    # simple dummy weather data
    return {
        "source": "fallback",
        "city": city,
        "current": {"temp": 30, "description": "clear sky", "humidity": 50, "wind": 10},
        "daily": [
            {"date": "2025-10-28", "temp_min": 25, "temp_max": 32, "condition": "sunny"},
            {"date": "2025-10-29", "temp_min": 26, "temp_max": 33, "condition": "cloudy"},
            {"date": "2025-10-30", "temp_min": 24, "temp_max": 31, "condition": "rainy"},
            {"date": "2025-10-31", "temp_min": 25, "temp_max": 32, "condition": "sunny"},
            {"date": "2025-11-01", "temp_min": 26, "temp_max": 34, "condition": "cloudy"},
        ]
    }


# ---------- Fetch news from RSS feeds ----------
def fetch_weather_news(feeds=WEATHER_NEWS_FEEDS, max_items=6):
    items = []
    for feed in feeds:
        try:
            parsed = feedparser.parse(feed)
            for entry in parsed.entries[:max_items]:
                pub = getattr(entry, "published", "") or getattr(entry, "updated", "")
                items.append({
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", "#"),
                    "published": pub,
                    "summary": getattr(entry, "summary", "")[:250]
                })
        except Exception:
            continue
    return items[:max_items]


# ---------- Main View ----------
def project_price_with_weather(request):
        city = request.GET.get("city", DEFAULT_CITY)

        # Try API
        forecast = fetch_forecast_via_api(city)
        if not forecast:
            # fallback dummy
            forecast = fetch_forecast_fallback(city)

        news_items = fetch_weather_news()

        context = {
            "forecast": forecast,
            "news_items": news_items,
            "requested_city": city,
            "now": timezone.now()
        }
        print(context)
        return render(request, "myapp/webscrapping.html", context)

def karachi_live_weather(request):
    """Fetch Karachi's current temperature and 24-hour forecast"""
    api_key = "30f32fd8eb1ec1c3f7a1efad953498c1"  # Free OpenWeatherMap key
    city = "Karachi"

    try:
        # Current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        current_data = requests.get(url, timeout=10).json()
        current_temp = current_data["main"]["temp"]
        description = current_data["weather"][0]["description"].title()
        humidity = current_data["main"]["humidity"]
        wind = current_data["wind"]["speed"]

        # 24-hour forecast (OpenWeatherMap gives 3-hour intervals)
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        forecast_data = requests.get(forecast_url, timeout=10).json()

        hourly_labels = []
        hourly_temps = []
        for item in forecast_data["list"][:8]:  # 8 intervals = 24 hours
            timestamp = item["dt"]
            time_str = time.strftime("%I:%M %p", time.localtime(timestamp))
            hourly_labels.append(time_str)
            hourly_temps.append(item["main"]["temp"])

        context = {
            "city": city,
            "current_temp": current_temp,
            "description": description,
            "humidity": humidity,
            "wind": wind,
            "labels": hourly_labels,
            "temps": hourly_temps,
        }

    except Exception as e:
        print("Weather fetch error:", e)
        context = {
            "city": city,
            "error": "Unable to load live weather data at this moment.",
        }

    return render(request, "index.html", context)


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Authenticate with Firebase using email and password
            user = auth.get_user_by_email(email)  # Firebase user lookup by email
        except firebase_admin.auth.UserNotFoundError:
            messages.error(request, "No such user registered with this email.")
            return redirect("admin_login")

        try:
            # If Firebase authentication is successful, check the Admin collection in Firestore
            admin_ref = db.collection("Admin").document(email)  # Firebase document based on email
            admin_doc = admin_ref.get()

            if admin_doc.exists:
                # Verify the password in Firebase (This assumes Firebase is being used for authentication)
                if user.email == email:
                    # Log the user in
                    login(request, user)  # Using Django's session to log in
                    return redirect("Admin")  # Redirect to your actual admin dashboard URL
                else:
                    messages.error(request, "Incorrect password.")
                    return redirect("admin_login")
            else:
                messages.error(request, "You are not authorized to access the admin panel.")
                return redirect("admin_login")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("admin_login")

    return render(request, "myapp/admin_login.html")
