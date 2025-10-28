
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


def webscrapping (request):
    return render(request,"myapp/webscrapping.html")

OWM_API_KEY = "30f32fd8eb1ec1c3f7a1efad953498c1"
DEFAULT_CITY = os.getenv("WEATHER_CITY", "Karachi")  # default city
# Example RSS feeds for weather news (you can replace with site-specific feeds)
WEATHER_NEWS_FEEDS = [
    "https://www.dawn.com/latest-news",            # placeholder - replace with a real feed URL
    "https://www.weather.gov/rss_page.php?site_name=nws"  # placeholder
]

def fetch_forecast_via_api(city=DEFAULT_CITY, api_key=OWM_API_KEY):
    """Use OpenWeatherMap (Current + 5-day/3-hour forecast) if API key is present."""
    if not api_key:
        return None
    try:
        # Current weather
        cur_url = "https://api.openweathermap.org/data/2.5/weather"
        cur_params = {"q": city, "appid": api_key, "units": "metric"}
        cur_res = requests.get(cur_url, params=cur_params, timeout=8)
        cur_res.raise_for_status()
        current = cur_res.json()

        # 5-day forecast (3-hourly)
        f_url = "https://api.openweathermap.org/data/2.5/forecast"
        f_params = {"q": city, "appid": api_key, "units": "metric"}
        f_res = requests.get(f_url, params=f_params, timeout=8)
        f_res.raise_for_status()
        forecast = f_res.json()

        # Simplify forecast to daily summary (basic)
        daily = {}
        for item in forecast.get("list", []):
            dt_txt = item.get("dt_txt")  # "2025-10-25 12:00:00"
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
            "city": current.get("name"),
            "current": {
                "temp": current["main"]["temp"],
                "description": current["weather"][0]["description"],
                "humidity": current["main"]["humidity"],
                "wind": current["wind"]["speed"]
            },
            "daily": daily_summary[:5]  # first 5 days
        }
    except Exception as e:
        # log exception in real app
        return None


def fetch_forecast_via_scrape(city=DEFAULT_CITY):
    """
    Scrape weather data from BBC Weather (as a fallback if API fails).
    """
    try:
        city_slug = city.lower().replace(" ", "-")
        TARGET_URL = f"https://www.bbc.com/weather/{city_slug}"

        res = requests.get(TARGET_URL, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # BBC selectors
        current_temp = soup.select_one(".wr-value--temperature--c")
        current_desc = soup.select_one(".wr-day__weather-type-description")

        current = {
            "temp": current_temp.get_text(strip=True) if current_temp else "N/A",
            "description": current_desc.get_text(strip=True) if current_desc else "N/A"
        }

        daily_summary = []
        days = soup.select(".wr-day")
        for d in days[:5]:
            date = d.select_one(".wr-date").get_text(strip=True) if d.select_one(".wr-date") else ""
            tmax = d.select_one(".wr-day-temperature__high-value").get_text(strip=True) if d.select_one(".wr-day-temperature__high-value") else ""
            tmin = d.select_one(".wr-day-temperature__low-value").get_text(strip=True) if d.select_one(".wr-day-temperature__low-value") else ""
            cond = d.select_one(".wr-day__weather-type-description").get_text(strip=True) if d.select_one(".wr-day__weather-type-description") else ""
            daily_summary.append({
                "date": date,
                "temp_min": tmin,
                "temp_max": tmax,
                "condition": cond
            })

        return {
            "source": "scrape",
            "city": city,
            "current": current,
            "daily": daily_summary
        }
    except Exception as e:
        print("Scraping failed:", e)
        return None



def fetch_weather_news(feeds=WEATHER_NEWS_FEEDS, max_items=6):
    """
    Fetch news/blog items from a list of RSS feeds using feedparser.
    Returns list of {title, link, published, summary}
    """
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
    # sort by published if possible
    # best-effort: entries may have different formats; keep as-is
    return items[:max_items]


def project_price_with_weather(request):
    """
    Main view to render the existing template with weather + news/blogs data injected.
    """
    city = request.GET.get("city", DEFAULT_CITY)

    # 1) Try API first (recommended)
    forecast = fetch_forecast_via_api(city)

    # 2) If API unavailable, fallback to scraping (you must set valid selectors)
    if not forecast:
        forecast = fetch_forecast_via_scrape(city)

    # 3) Fetch news/blogs via RSS feeds
    news_items = fetch_weather_news()

    # 4) Build context for template
    context = {
        "forecast": forecast,
        "news_items": news_items,
        "requested_city": city,
        "now": datetime.utcnow()
    }
    return render(request, "project_price_weather.html", context)