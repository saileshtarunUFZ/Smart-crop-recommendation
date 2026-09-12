import sys
import os
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db.warning=false;qt.qpa.fonts.warning=false"

import csv
import requests
import webbrowser
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QStackedWidget,
    QFrame, QDialog, QMessageBox, QGroupBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
USERS_CSV = "users.csv"
MANDI_CACHE_CSV = "mandi_cache.csv"
SOIL_HEALTH_CSV = "soil_health.csv"
DATA_GOV_API_KEY = "YOUR_DATA_GOV_IN_API_KEY"
AGMARKNET_ENDPOINT = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

APP_FONT = "Nirmala UI"

MONTHS_LIST = [
    ("January", "Jan"), ("February", "Feb"), ("March", "Mar"),
    ("April", "Apr"), ("May", "May"), ("June", "Jun"),
    ("July", "Jul"), ("August", "Aug"), ("September", "Sep"),
    ("October", "Oct"), ("November", "Nov"), ("December", "Dec")
]

SEASON_RAINFALL_MAP = {
    "June": {"season": "Kharif (Monsoon Sowing)", "rainfall_level": "High (800-1200 mm)", "risk": "Waterlogging & Fungal Attack"},
    "July": {"season": "Kharif (Monsoon)", "rainfall_level": "High (900-1400 mm)", "risk": "Waterlogging & Pest Surge"},
    "August": {"season": "Kharif (Peak Monsoon)", "rainfall_level": "High (850-1300 mm)", "risk": "Leaf Blight & Insect Vectors"},
    "September": {"season": "Late Kharif (Retreating)", "rainfall_level": "Moderate (400-700 mm)", "risk": "Early Harvest Moisture Damage"},
    "October": {"season": "Post-Monsoon Transition", "rainfall_level": "Low-Moderate (100-250 mm)", "risk": "Delayed Sowing / Stubble Smog"},
    "November": {"season": "Rabi (Wheat Sowing)", "rainfall_level": "Low (< 50 mm)", "risk": "Soil Moisture Depletion"},
    "December": {"season": "Rabi Growth (Winter)", "rainfall_level": "Dry / Light Showers (< 30 mm)", "risk": "Frost & Yellow Rust"},
    "January": {"season": "Rabi (Peak Winter)", "rainfall_level": "Light Showers (< 40 mm)", "risk": "Cold Wave & Yellow Rust"},
    "February": {"season": "Rabi (Late Winter)", "rainfall_level": "Dry (< 25 mm)", "risk": "Aphid Attacks"},
    "March": {"season": "Rabi Harvest", "rainfall_level": "Dry (< 20 mm)", "risk": "Sudden Heatwave / Premature Drying"},
    "April": {"season": "Zaid (Summer Sowing)", "rainfall_level": "Very Dry / Hot (< 15 mm)", "risk": "Severe Heat & Water Scarcity"},
    "May": {"season": "Zaid / Pre-Monsoon", "rainfall_level": "Dry / Storms (< 30 mm)", "risk": "Extreme Heat Stress"}
}

def init_csv_files():
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "email", "mobile", "district", "land"])

    if not os.path.exists(MANDI_CACHE_CSV) or os.path.getsize(MANDI_CACHE_CSV) == 0:
        with open(MANDI_CACHE_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["district", "mandi", "commodity", "min_price", "max_price", "modal_price"])
            default_mandi_data = [
                ["Ludhiana", "Khanna Mandi", "Wheat (HD-3086)", 2350, 2600, 2550],
                ["Ludhiana", "Ludhiana Main", "Paddy (PR-126)", 2180, 2320, 2250],
                ["Ludhiana", "Jagraon Mandi", "Potato", 900, 1200, 1050],
                ["Ludhiana", "Khanna Mandi", "Maize", 2050, 2200, 2120],
                ["Bathinda", "Bathinda Grain Market", "Cotton (Bt Cotton)", 6800, 7400, 7150],
                ["Bathinda", "Maur Mandi", "Wheat", 2450, 2590, 2520],
                ["Bathinda", "Bathinda Main", "Paddy (PR-126)", 2150, 2280, 2200],
                ["Bathinda", "Raman Mandi", "Guar", 4800, 5300, 5050],
                ["Sangrur", "Sangrur Main", "Basmati Rice (1121)", 3800, 4400, 4100],
                ["Sangrur", "Sunam Mandi", "Sugarcane", 380, 395, 390],
                ["Sangrur", "Dhuri Mandi", "Wheat", 2480, 2600, 2540],
                ["Sangrur", "Ahmedgarh", "Mustard", 5100, 5600, 5350],
                ["Amritsar", "Amritsar Bhagtanwala", "Basmati Rice (1509)", 3400, 3900, 3700],
                ["Amritsar", "Majitha Mandi", "Basmati Rice (1121)", 3900, 4500, 4200],
                ["Amritsar", "Jandiala Guru", "Wheat", 2500, 2620, 2560],
                ["Amritsar", "Amritsar Main", "Vegetables (Tomato/Onion)", 1800, 2500, 2100]
            ]
            writer.writerows(default_mandi_data)

    if not os.path.exists(SOIL_HEALTH_CSV):
        with open(SOIL_HEALTH_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["district", "nitrogen", "phosphorus", "potassium", "pH", "ec"])
            writer.writerows([
                ["Ludhiana", 210, 18, 135, 7.8, 0.35],
                ["Bathinda", 180, 12, 290, 8.4, 1.25],
                ["Sangrur", 230, 22, 150, 7.6, 0.40],
                ["Amritsar", 260, 28, 175, 7.4, 0.28]
            ])

init_csv_files()

TRANSLATIONS = {
    "en": {
        "app_title": "AgriSmart Punjab - Advisory & Mandi Portal",
        "nav_advisor": "🌱 Crop & Water Advisor",
        "nav_mandi": "📊 Punjab Mandi Data",
        "nav_portal_link": "🔗 Punjab e-Mandi Portal (Google)",
        "banner_welcome": "Welcome back, Punjab Farmer Friend!",
        "banner_sub": "Punjab-specific crop insights, seasonal rainfall management, pesticide usage & govt schemes.",
        "district_label": "Select District:",
        "month_label": "Select Sowing Month:",
        "land_label": "Enter Land Size (Acres):",
        "login_btn": "User Account / Login",
        "logout_btn": "Logout",
        "calc_btn": "Analyze Season & Crops",
        "export_btn": "📄 Export Advisory Report",
        "mandi_search_ph": "Search commodity or mandi...",
        "mandi_filter_all": "All Commodities"
    },
    "pa": {
        "app_title": "ਐਗਰੀਸਮਾਰਟ ਪੰਜਾਬ - ਸਲਾਹਕਾਰ ਅਤੇ ਮੰਡੀ ਪੋਰਟਲ",
        "nav_advisor": "🌱 ਫਸਲ ਅਤੇ ਪਾਣੀ ਦੀ ਸਲਾਹ",
        "nav_mandi": "📊 ਪੰਜਾਬ ਮੰਡੀ ਡੇਟਾ",
        "nav_portal_link": "🔗 ਪੰਜਾਬ ਈ-ਮੰਡੀ ਪੋਰਟਲ (Google)",
        "banner_welcome": "ਜੀ ਆਇਆਂ ਨੂੰ, ਪੰਜਾਬ ਦੇ ਕਿਸਾਨ ਵੀਰੋ!",
        "banner_sub": "ਪੰਜਾਬ-ਵਿਸ਼ੇਸ਼ ਫਸਲਾਂ ਦੀ ਜਾਣਕਾਰੀ, ਮੌਸਮੀ ਬਾਰਿਸ਼, ਕੀਟਨਾਸ਼ਕਾਂ ਦੀ ਵਰਤੋਂ ਅਤੇ ਸਰਕਾਰੀ ਸਕੀਮਾਂ।",
        "district_label": "ਜ਼ਿਲ੍ਹਾ ਚੁਣੋ:",
        "month_label": "ਬਿਜਾਈ ਦਾ ਮਹੀਨਾ ਚੁਣੋ:",
        "land_label": "ਜ਼ਮੀਨ ਦਾ ਆਕਾਰ (ਏਕੜ):",
        "login_btn": "ਉਪਭੋਗਤਾ ਖਾਤਾ / ਲੌਗਇਨ",
        "logout_btn": "ਲੌਗਆਊਟ",
        "calc_btn": "ਮੌਸਮ ਅਤੇ ਫਸਲਾਂ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ",
        "export_btn": "📄 ਰਿਪੋਰਟ ਐਕਸਪੋਰਟ ਕਰੋ",
        "mandi_search_ph": "ਫਸਲ ਜਾਂ ਮੰਡੀ ਲੱਭੋ...",
        "mandi_filter_all": "ਸਾਰੀਆਂ ਫਸਲਾਂ"
    },
    "hi": {
        "app_title": "एग्रीस्मार्ट पंजाब - सलाह एवं मंडी पोर्टल",
        "nav_advisor": "🌱 फसल एवं जल सलाह",
        "nav_mandi": "📊 पंजाब मंडी डेटा",
        "nav_portal_link": "🔗 पंजाब ई-मंडी पोर्टल (Google)",
        "banner_welcome": "फिर से स्वागत है, पंजाब के किसान मित्र!",
        "banner_sub": "पंजाब-विशिष्ट फसल अंतर्दृष्टि, मौसमी वर्षा, कीटनाशक उपयोग और सरकारी योजनाएं।",
        "district_label": "जिला चुनें:",
        "month_label": "बुवाई का महीना चुनें:",
        "land_label": "भूमि का आकार (एकड़):",
        "login_btn": "उपयोगकर्ता खाता / लॉगिन",
        "logout_btn": "लॉगआउट",
        "calc_btn": "मौसम और फसलों का विश्लेषण करें",
        "export_btn": "📄 रिपोर्ट निर्यात करें",
        "mandi_search_ph": "फसल या मंडी खोजें...",
        "mandi_filter_all": "सभी फसलें"
    }
}

def save_user_to_csv(name, email, mobile, district, land=5.0):
    if find_user_by_email(email):
        return False, "Email already registered."
    with open(USERS_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, email, mobile, district, land])
    return True, "User registered successfully."

def find_user_by_email(email):
    if not os.path.exists(USERS_CSV):
        return None
    with open(USERS_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["email"].strip().lower() == email.strip().lower():
                return row
    return None

def save_mandi_prices_to_csv(records):
    existing_records = []
    if os.path.exists(MANDI_CACHE_CSV):
        with open(MANDI_CACHE_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_records = list(reader)

    new_lookup = {(r["district"], r["mandi"], r["commodity"]): r for r in records}
    updated_records = []
    
    for row in existing_records:
        key = (row["district"], row["mandi"], row["commodity"])
        if key in new_lookup:
            updated_records.append(new_lookup.pop(key))
        else:
            updated_records.append(row)

    for remaining in new_lookup.values():
        updated_records.append(remaining)

    with open(MANDI_CACHE_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["district", "mandi", "commodity", "min_price", "max_price", "modal_price"])
        writer.writeheader()
        for r in updated_records:
            writer.writerow({
                "district": r["district"],
                "mandi": r["mandi"],
                "commodity": r["commodity"],
                "min_price": r["min_price"],
                "max_price": r["max_price"],
                "modal_price": r["modal_price"]
            })

def get_mandi_prices_from_csv(district):
    records = []
    if not os.path.exists(MANDI_CACHE_CSV):
        return records

    with open(MANDI_CACHE_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["district"].strip().lower() == district.strip().lower():
                records.append({
                    "mandi": row["mandi"],
                    "district": row["district"],
                    "commodity": row["commodity"],
                    "min_price": float(row["min_price"]),
                    "max_price": float(row["max_price"]),
                    "modal_price": float(row["modal_price"])
                })
    return records

def get_soil_data_from_csv(district):
    if os.path.exists(SOIL_HEALTH_CSV):
        with open(SOIL_HEALTH_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["district"].strip().lower() == district.strip().lower():
                    return {
                        "nitrogen": float(row["nitrogen"]),
                        "phosphorus": float(row["phosphorus"]),
                        "potassium": float(row["potassium"]),
                        "pH": float(row["pH"]),
                        "ec": float(row["ec"])
                    }
    return {"nitrogen": 200.0, "phosphorus": 15.0, "potassium": 150.0, "pH": 7.5, "ec": 0.5}

def calculate_seasonal_crop_probability(crop_name, base_probability, soil_params, month_name):
    adjusted = base_probability
    ph = soil_params.get("pH", 7.0)
    nitrogen = soil_params.get("nitrogen", 250)
    
    month_info = SEASON_RAINFALL_MAP.get(month_name, {})
    season = month_info.get("season", "")

    if "Paddy" in crop_name or "Rice" in crop_name:
        if "Kharif" in season:
            adjusted += 5
        else:
            adjusted -= 30
        if ph > 8.0:
            adjusted -= 10
    elif "Wheat" in crop_name:
        if "Rabi" in season:
            adjusted += 5
        else:
            adjusted -= 35
        if nitrogen < 200:
            adjusted -= 8
    elif "Cotton" in crop_name:
        if month_name in ["April", "May", "June"]:
            adjusted += 5
        else:
            adjusted -= 20

    return max(0, min(100, int(adjusted)))

class MandiApiThread(QThread):
    data_fetched = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, district):
        super().__init__()
        self.district = district

    def run(self):
        try:
            params = {
                "api-key": DATA_GOV_API_KEY,
                "format": "json",
                "offset": 0,
                "limit": 50,
                "filters[state]": "Punjab",
                "filters[district]": self.district
            }
            response = requests.get(AGMARKNET_ENDPOINT, params=params, timeout=6)
            if response.status_code == 200:
                data = response.json()
                records = []
                for rec in data.get("records", []):
                    records.append({
                        "mandi": rec.get("market", "Unknown Market"),
                        "district": rec.get("district", self.district),
                        "commodity": rec.get("commodity", "N/A"),
                        "min_price": float(rec.get("min_price", 0)),
                        "max_price": float(rec.get("max_price", 0)),
                        "modal_price": float(rec.get("modal_price", 0))
                    })
                self.data_fetched.emit(records)
            else:
                self.error_occurred.emit(f"HTTP Status {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(str(e))

ENHANCED_DISTRICT_DATA = {
    "Ludhiana": [
        {
            "crop": "Paddy (PR-126)",
            "base_probability": 88,
            "water_consumption": "High (~1200 mm, 18-20 irrigations required)",
            "pesticide_types": "Pre-emergence Herbicide (Pretilachlor), Insecticide (Cartap Hydrochloride)",
            "pesticide_usage_rate": "1.8 kg/acre active ingredient",
            "emergency_scenario": "Groundwater depletion / Planthopper infestation during late rains.",
            "schemes": ["Direct Sown Rice (DSR) Incentive (₹1,500/acre)", "Pani Bachao, Paise Kamao Scheme", "CRM Machinery Subsidy"]
        },
        {
            "crop": "Wheat (HD-3086)",
            "base_probability": 92,
            "water_consumption": "Moderate (~400 mm, 4-5 irrigations required)",
            "pesticide_types": "Fungicide (Tebuconazole / Propiconazole for Yellow Rust)",
            "pesticide_usage_rate": "0.8 kg/acre active ingredient",
            "emergency_scenario": "Sudden March heatwaves causing premature grain shriveling.",
            "schemes": ["PM-KISAN (₹6,000/yr)", "Sub-Mission on Agricultural Mechanization"]
        }
    ],
    "Bathinda": [
        {
            "crop": "Cotton (Bt Cotton)",
            "base_probability": 82,
            "water_consumption": "Moderate-Low (~600 mm, drip-friendly)",
            "pesticide_types": "Systemic Insecticides (Flonicamid, Spinetoram for Pink Bollworm/Whitefly)",
            "pesticide_usage_rate": "2.5 kg/acre active ingredient",
            "emergency_scenario": "Pink Bollworm resistant outbreak or canal water cuts during boll formation.",
            "schemes": ["Cotton Seed Subsidy Scheme", "PMKSY Drip Irrigation Subsidy (80%)"]
        },
        {
            "crop": "Wheat",
            "base_probability": 90,
            "water_consumption": "Moderate (~400 mm, 4-5 irrigations)",
            "pesticide_types": "Herbicides (Clodinafop-propargyl for Phalaris minor)",
            "pesticide_usage_rate": "0.9 kg/acre active ingredient",
            "emergency_scenario": "Gulli Danda herbicide resistance resulting in high weed pressure.",
            "schemes": ["National Food Security Mission (NFSM)", "Soil Health Card Scheme"]
        }
    ],
    "Sangrur": [
        {
            "crop": "Basmati Rice (1121)",
            "base_probability": 85,
            "water_consumption": "High (~1000 mm)",
            "pesticide_types": "Bio-pesticides, Tricyclazole",
            "pesticide_usage_rate": "1.2 kg/acre active ingredient",
            "emergency_scenario": "Bacterial Leaf Blight combined with pesticide residue export rejection risks.",
            "schemes": ["Punjab Crop Diversification Mission", "Export Basmati Registration Portal"]
        }
    ],
    "Amritsar": [
        {
            "crop": "Basmati Rice (1509)",
            "base_probability": 89,
            "water_consumption": "Medium-High (~900 mm)",
            "pesticide_types": "Azoxystrobin for Stem Rot & Sheath Blight",
            "pesticide_usage_rate": "1.1 kg/acre active ingredient",
            "emergency_scenario": "Unseasonal harvest rains causing grain discoloration.",
            "schemes": ["RKVY Organic Inputs Subsidy", "Punjab Agri Export Support"]
        }
    ]
}

class LanguageSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_language = "pa"
        self.setWindowTitle("Language Selection / ਭਾਸ਼ਾ ਚੋਣ")
        self.setFixedSize(380, 240)
        self.setStyleSheet("background-color: #f8fafc;")

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel(TRANSLATIONS["pa"]["lang_select_title"])
        title.setFont(QFont(APP_FONT, 11, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        prompt = QLabel(TRANSLATIONS["pa"]["lang_select_prompt"])
        prompt.setFont(QFont(APP_FONT, 10))
        prompt.setWordWrap(True)
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(prompt)

        self.lang_combo = QComboBox()
        self.lang_combo.setFont(QFont(APP_FONT, 10))
        self.lang_combo.addItem("ਪੰਜਾਬੀ (Punjabi)", "pa")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("हिंदी (Hindi)", "hi")
        self.lang_combo.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px;")
        layout.addWidget(self.lang_combo)

        confirm_btn = QPushButton(TRANSLATIONS["pa"]["confirm"])
        confirm_btn.setFont(QFont(APP_FONT, 10, QFont.Weight.Bold))
        confirm_btn.setStyleSheet("background-color: #16a34a; color: white; padding: 10px; border-radius: 6px;")
        confirm_btn.clicked.connect(self.on_confirm)
        layout.addWidget(confirm_btn)

    def on_confirm(self):
        self.selected_language = self.lang_combo.currentData()
        self.accept()


class DualLoginDialog(QDialog):
    def __init__(self, parent=None, current_lang="pa"):
        super().__init__(parent)
        self.current_lang = current_lang
        self.user_profile = None

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("Punjab Farmer Portal - Access")
        self.setFixedSize(420, 480)
        self.setStyleSheet("background-color: #ffffff;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        self.tabs = QTabWidget()
        self.tabs.setFont(QFont(APP_FONT, 9, QFont.Weight.Bold))

        exist_widget = QWidget()
        exist_layout = QVBoxLayout(exist_widget)
        exist_layout.addWidget(QLabel("<b>Registered Email ID:</b>"))
        self.exist_email_input = QLineEdit()
        self.exist_email_input.setPlaceholderText("farmer@example.com")
        self.exist_email_input.setStyleSheet("padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px;")
        exist_layout.addWidget(self.exist_email_input)

        btn_login = QPushButton("Verify CSV & Login")
        btn_login.setStyleSheet("background-color: #15803d; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_login.clicked.connect(self.handle_exist_login)
        exist_layout.addWidget(btn_login)
        exist_layout.addStretch()

        new_widget = QWidget()
        new_layout = QVBoxLayout(new_widget)
        new_layout.addWidget(QLabel("<b>Full Name:</b>"))
        self.reg_name = QLineEdit()
        self.reg_name.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px;")
        new_layout.addWidget(self.reg_name)

        new_layout.addWidget(QLabel("<b>Mobile Number:</b>"))
        self.reg_mobile = QLineEdit()
        self.reg_mobile.setMaxLength(10)
        self.reg_mobile.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px;")
        new_layout.addWidget(self.reg_mobile)

        new_layout.addWidget(QLabel("<b>District & Landholding (Acres):</b>"))
        dist_row = QHBoxLayout()
        self.reg_district = QComboBox()
        self.reg_district.addItems(ENHANCED_DISTRICT_DATA.keys())
        self.reg_district.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px;")
        
        self.reg_land = QDoubleSpinBox()
        self.reg_land.setRange(0.5, 500.0)
        self.reg_land.setValue(5.0)
        self.reg_land.setSuffix(" Acres")
        self.reg_land.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px;")

        dist_row.addWidget(self.reg_district)
        dist_row.addWidget(self.reg_land)
        new_layout.addLayout(dist_row)

        new_layout.addWidget(QLabel("<b>Email Address:</b>"))
        self.reg_email = QLineEdit()
        self.reg_email.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 6px;")
        new_layout.addWidget(self.reg_email)

        btn_register = QPushButton("Save Account to CSV & Login")
        btn_register.setStyleSheet("background-color: #16a34a; color: white; padding: 10px; border-radius: 6px; font-weight: bold;")
        btn_register.clicked.connect(self.handle_reg_submit)
        new_layout.addWidget(btn_register)

        self.tabs.addTab(exist_widget, " Existing User Login")
        self.tabs.addTab(new_widget, " New User Registration")
        layout.addWidget(self.tabs)

    def handle_exist_login(self):
        email = self.exist_email_input.text().strip()
        user = find_user_by_email(email)
        if user:
            self.user_profile = user
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "User not found in users.csv file.")

    def handle_reg_submit(self):
        name = self.reg_name.text().strip()
        mobile = self.reg_mobile.text().strip()
        email = self.reg_email.text().strip()
        district = self.reg_district.currentText()
        land = self.reg_land.value()

        if not name or len(mobile) < 10 or not email or "@" not in email:
            QMessageBox.warning(self, "Error", "Please fill in all fields correctly.")
            return

        success, msg = save_user_to_csv(name, email, mobile, district, land)
        if success:
            self.user_profile = {"name": name, "email": email, "mobile": mobile, "district": district, "land": land}
            self.accept()
        else:
            QMessageBox.warning(self, "Error", msg)


class MainApp(QMainWindow):
    def __init__(self, initial_lang="pa", initial_user=None):
        super().__init__()
        self.current_lang = initial_lang
        self.logged_in_user = initial_user
        self.init_ui()

    def init_ui(self):
        self.resize(1150, 850)
        self.setStyleSheet("QMainWindow { background-color: #f1f5f9; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        self.build_navbar()
        self.build_banner()

        # Selection Control Frame
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; padding: 10px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)

        self.lbl_district = QLabel()
        self.combo_district = QComboBox()
        self.combo_district.addItems(ENHANCED_DISTRICT_DATA.keys())
        self.combo_district.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.combo_district.currentIndexChanged.connect(self.on_selection_changed)

        self.lbl_month = QLabel()
        self.combo_month = QComboBox()
        for m_name, m_short in MONTHS_LIST:
            self.combo_month.addItem(m_name, m_name)
        self.combo_month.setCurrentText("June")
        self.combo_month.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.combo_month.currentIndexChanged.connect(self.on_selection_changed)

        self.lbl_land = QLabel()
        self.spin_land = QDoubleSpinBox()
        self.spin_land.setRange(0.5, 500.0)
        self.spin_land.setValue(5.0)
        self.spin_land.setSuffix(" Acres")
        self.spin_land.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")

        self.btn_calculate = QPushButton()
        self.btn_calculate.setStyleSheet("background-color: #16a34a; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        self.btn_calculate.clicked.connect(self.on_selection_changed)

        self.btn_export = QPushButton()
        self.btn_export.setStyleSheet("background-color: #0284c7; color: white; padding: 8px 16px; border-radius: 6px; font-weight: bold;")
        self.btn_export.clicked.connect(self.export_advisory_report)

        ctrl_layout.addWidget(self.lbl_district)
        ctrl_layout.addWidget(self.combo_district)
        ctrl_layout.addSpacing(10)
        ctrl_layout.addWidget(self.lbl_month)
        ctrl_layout.addWidget(self.combo_month)
        ctrl_layout.addSpacing(10)
        ctrl_layout.addWidget(self.lbl_land)
        ctrl_layout.addWidget(self.spin_land)
        ctrl_layout.addSpacing(10)
        ctrl_layout.addWidget(self.btn_calculate)
        ctrl_layout.addWidget(self.btn_export)

        self.main_layout.addWidget(ctrl_frame)

        # Seasonal Rainfall Overview Card
        self.season_box = QGroupBox("🌧️ Seasonal Rainfall & Climate Profile")
        self.season_box.setStyleSheet("QGroupBox { font-weight: bold; background-color: #ffffff; border-radius: 8px; padding: 10px; }")
        season_layout = QVBoxLayout(self.season_box)
        self.lbl_season_info = QLabel()
        self.lbl_season_info.setWordWrap(True)
        season_layout.addWidget(self.lbl_season_info)
        self.main_layout.addWidget(self.season_box)

        # Tab Widget View (Advisor & Mandi Pages)
        self.stacked_widget = QStackedWidget()
        self.advisor_page = self.build_punjab_advisor_page()
        self.mandi_page = self.build_mandi_rates_page()

        self.stacked_widget.addWidget(self.advisor_page)
        self.stacked_widget.addWidget(self.mandi_page)
        self.main_layout.addWidget(self.stacked_widget)

        if self.logged_in_user:
            dist = self.logged_in_user.get("district")
            land = self.logged_in_user.get("land")
            if dist:
                idx = self.combo_district.findText(dist)
                if idx != -1:
                    self.combo_district.setCurrentIndex(idx)
            if land:
                self.spin_land.setValue(float(land))

        self.update_language_texts()

    def build_navbar(self):
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; padding: 6px;")
        nav_layout = QHBoxLayout(nav_frame)

        self.brand_label = QLabel("🌾 AgriSmart Punjab")
        self.brand_label.setFont(QFont(APP_FONT, 14, QFont.Weight.Bold))
        self.brand_label.setStyleSheet("color: #15803d; margin-right: 15px;")
        nav_layout.addWidget(self.brand_label)

        self.btn_advisor = QPushButton()
        self.btn_mandi = QPushButton()
        
        for btn, idx in [(self.btn_advisor, 0), (self.btn_mandi, 1)]:
            btn.setStyleSheet("QPushButton { border: none; padding: 8px 12px; font-weight: 600; color: #475569; } QPushButton:hover { color: #16a34a; background-color: #f0fdf4; border-radius: 4px; }")
            btn.clicked.connect(lambda _, i=idx: self.stacked_widget.setCurrentIndex(i))
            nav_layout.addWidget(btn)

        self.btn_google_portal = QPushButton()
        self.btn_google_portal.setStyleSheet("QPushButton { background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 6px 12px; border-radius: 6px; font-weight: 600; margin-left: 10px; }")
        self.btn_google_portal.clicked.connect(lambda: webbrowser.open("https://www.google.com/search?q=punjab+mandi+board+login"))
        nav_layout.addWidget(self.btn_google_portal)

        nav_layout.addStretch()

        self.btn_login = QPushButton()
        self.btn_login.setStyleSheet("QPushButton { background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; font-weight: 600; }")
        self.btn_login.clicked.connect(self.open_login_dialog)
        nav_layout.addWidget(self.btn_login)

        self.btn_logout = QPushButton()
        self.btn_logout.setStyleSheet("QPushButton { background-color: #fef2f2; color: #dc2626; border: 1px solid #fca5a5; padding: 6px 12px; border-radius: 6px; font-weight: 600; }")
        self.btn_logout.clicked.connect(self.handle_logout)
        nav_layout.addWidget(self.btn_logout)

        self.lang_dropdown = QComboBox()
        self.lang_dropdown.addItem("ਪੰਜਾਬੀ", "pa")
        self.lang_dropdown.addItem("English", "en")
        self.lang_dropdown.addItem("हिंदी", "hi")
        index = self.lang_dropdown.findData(self.current_lang)
        if index != -1:
            self.lang_dropdown.setCurrentIndex(index)
        self.lang_dropdown.currentIndexChanged.connect(self.on_language_change)
        self.lang_dropdown.setStyleSheet("padding: 4px 8px; border: 1px solid #cbd5e1; border-radius: 4px;")
        nav_layout.addWidget(self.lang_dropdown)

        self.main_layout.addWidget(nav_frame)

    def build_banner(self):
        banner_frame = QFrame()
        banner_frame.setStyleSheet("background-color: #15803d; border-radius: 10px; color: white; padding: 15px;")
        banner_layout = QVBoxLayout(banner_frame)

        self.banner_title = QLabel()
        self.banner_title.setFont(QFont(APP_FONT, 15, QFont.Weight.Bold))
        self.banner_sub = QLabel()
        self.banner_sub.setFont(QFont(APP_FONT, 10))
  
        banner_layout.addWidget(self.banner_title)
        banner_layout.addWidget(self.banner_sub)
        self.main_layout.addWidget(banner_frame)

    def build_punjab_advisor_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)

        # Left Side Layout (Crop List + Regional Mandi Market Prices Table)
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.crop_table = QTableWidget(0, 2)
        self.crop_table.setHorizontalHeaderLabels(["Crop Name", "Season Probability"])
        self.crop_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.crop_table.cellClicked.connect(self.display_crop_details)
        left_layout.addWidget(self.crop_table, 2)

        # Mandi Market Prices per Quintal Summary Box
        mandi_box = QGroupBox("📊 Regional Mandi Market Prices (₹ / Quintal)")
        mandi_box.setStyleSheet("QGroupBox { font-weight: bold; background-color: #ffffff; border-radius: 8px; padding: 6px; }")
        mandi_layout = QVBoxLayout(mandi_box)

        self.advisory_mandi_table = QTableWidget(0, 4)
        self.advisory_mandi_table.setHorizontalHeaderLabels(["Market", "Commodity", "Min (₹)", "Max (₹)"])
        self.advisory_mandi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        mandi_layout.addWidget(self.advisory_mandi_table)
        left_layout.addWidget(mandi_box, 3)

        layout.addWidget(left_container, 5)

        # Right Side Layout: Detailed Crop Breakdown (Fully visible without vertical cutoff)
        self.details_box = QGroupBox("Detailed Crop & Rainfall Management Breakdown")
        self.details_box.setStyleSheet("QGroupBox { background-color: #ffffff; border-radius: 8px; padding: 10px; font-weight: bold; }")
        self.details_layout = QVBoxLayout(self.details_box)

        self.lbl_crop_name = QLabel("<b>Select a crop from the table to view details.</b>")
        self.lbl_water = QLabel("<b>💧 Water Consumption:</b> -")
        self.lbl_pesticide = QLabel("<b>🛡️ Pesticide Protocols:</b> -")
        self.lbl_emergency = QLabel("<b>🚨 Emergency Scenario:</b> -")
        self.lbl_schemes = QLabel("<b>📜 Government Schemes:</b> -")

        for lbl in [self.lbl_crop_name, self.lbl_water, self.lbl_pesticide, self.lbl_emergency, self.lbl_schemes]:
            lbl.setFont(QFont(APP_FONT, 10))
            lbl.setWordWrap(True)
            self.details_layout.addWidget(lbl)

        self.details_layout.addStretch()
        layout.addWidget(self.details_box, 5)

        return page

    def build_mandi_rates_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #ffffff; border-radius: 8px; padding: 10px;")
        controls_layout = QHBoxLayout(controls_frame)

        self.mandi_search = QLineEdit()
        self.mandi_search.setPlaceholderText("Search commodity or mandi...")
        self.mandi_search.setStyleSheet("padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.mandi_search.textChanged.connect(self.filter_mandi_table)

        self.btn_refresh_api = QPushButton("🔄 Fetch Live Agmarknet Rates")
        self.btn_refresh_api.setStyleSheet("background-color: #16a34a; color: white; padding: 6px 12px; font-weight: bold;")
        self.btn_refresh_api.clicked.connect(self.fetch_live_mandi)

        controls_layout.addWidget(self.mandi_search)
        controls_layout.addWidget(self.btn_refresh_api)
        layout.addWidget(controls_frame)

        self.lbl_mandi_status = QLabel("Mandi Rates Status: Ready")
        layout.addWidget(self.lbl_mandi_status)

        self.mandi_table = QTableWidget(0, 6)
        self.mandi_table.setHorizontalHeaderLabels(["District", "Mandi Market", "Commodity", "Min Price (₹/Qtl)", "Max Price (₹/Qtl)", "Modal Price (₹/Qtl)"])
        self.mandi_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.mandi_table.setStyleSheet("QTableWidget { background-color: #ffffff; gridline-color: #e2e8f0; }")

        layout.addWidget(self.mandi_table)
        return page

    def on_selection_changed(self):
        district = self.combo_district.currentText()
        month = self.combo_month.currentText()
        soil = get_soil_data_from_csv(district)
        m_info = SEASON_RAINFALL_MAP.get(month, {})

        self.lbl_season_info.setText(
            f"<b>Month Selected:</b> {month} | <b>Agricultural Season:</b> {m_info.get('season')} | "
            f"<b>Expected Rainfall:</b> <span style='color: #1d4ed8;'>{m_info.get('rainfall_level')}</span><br>"
            f"<b>Primary Seasonal Risk:</b> <span style='color: #dc2626;'>{m_info.get('risk')}</span> | "
            f"<b>Soil Test (Card):</b> N={soil['nitrogen']} kg/ha, pH={soil['pH']}"
        )

        crops = ENHANCED_DISTRICT_DATA.get(district, [])
        self.crop_table.setRowCount(len(crops))

        for row, item in enumerate(crops):
            prob = calculate_seasonal_crop_probability(item["crop"], item["base_probability"], soil, month)
            self.crop_table.setItem(row, 0, QTableWidgetItem(item["crop"]))
            self.crop_table.setItem(row, 1, QTableWidgetItem(f"{prob}%"))

        if crops:
            self.crop_table.selectRow(0)
            self.display_crop_details(0, 0)

        self.load_advisory_mandi_prices(district)
        self.fetch_live_mandi()

    def load_advisory_mandi_prices(self, district):
        records = get_mandi_prices_from_csv(district)
        self.advisory_mandi_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.advisory_mandi_table.setItem(row, 0, QTableWidgetItem(rec["mandi"]))
            self.advisory_mandi_table.setItem(row, 1, QTableWidgetItem(rec["commodity"]))
            self.advisory_mandi_table.setItem(row, 2, QTableWidgetItem(str(rec["min_price"])))
            self.advisory_mandi_table.setItem(row, 3, QTableWidgetItem(str(rec["max_price"])))

    def display_crop_details(self, row, col):
        district = self.combo_district.currentText()
        crops = ENHANCED_DISTRICT_DATA.get(district, [])
        if row < len(crops):
            crop = crops[row]
            land_size = self.spin_land.value()
            self.lbl_crop_name.setText(f"<h2>{crop['crop']}</h2><hr>")
            self.lbl_water.setText(f"<b>💧 Water Consumption:</b><br>{crop['water_consumption']}")
            self.lbl_pesticide.setText(f"<b>🛡️ Pesticide Protocols:</b><br>{crop['pesticide_types']}<br><i>Total for {land_size} Acres: ~{round(2.0*land_size, 1)} kg active ingredient</i>")
            self.lbl_emergency.setText(f"<b>🚨 Emergency Scenario:</b><br>{crop['emergency_scenario']}")
            self.lbl_schemes.setText(f"<b>📜 Government Schemes:</b><br>" + "<br>• ".join([""] + crop['schemes']))

    def fetch_live_mandi(self):
        district = self.combo_district.currentText()
        self.lbl_mandi_status.setText("<i>Fetching live market data...</i>")
        self.thread = MandiApiThread(district)
        self.thread.data_fetched.connect(self.on_mandi_api_success)
        self.thread.error_occurred.connect(self.on_mandi_api_error)
        self.thread.start()

    def on_mandi_api_success(self, records):
        district = self.combo_district.currentText()
        if records:
            save_mandi_prices_to_csv(records)
            self.lbl_mandi_status.setText("<b style='color: green;'>Status: Showing Live Agmarknet Prices (Cached to CSV)</b>")
            self.populate_mandi_table(records)
            self.load_advisory_mandi_prices(district)
        else:
            self.fallback_to_csv(district, "Live API returned empty response.")

    def on_mandi_api_error(self, err_msg):
        district = self.combo_district.currentText()
        self.fallback_to_csv(district, f"Network offline ({err_msg}).")

    def fallback_to_csv(self, district, reason):
        cached = get_mandi_prices_from_csv(district)
        if cached:
            self.lbl_mandi_status.setText(f"<b style='color: orange;'>Status: Loaded Cached Mandi Rates from CSV ({reason})</b>")
            self.populate_mandi_table(cached)
            self.load_advisory_mandi_prices(district)
        else:
            self.lbl_mandi_status.setText(f"<b style='color: red;'>Status: Offline — No cached records found.</b>")
            self.mandi_table.setRowCount(0)

    def populate_mandi_table(self, records):
        self.mandi_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.mandi_table.setItem(row, 0, QTableWidgetItem(rec["district"]))
            self.mandi_table.setItem(row, 1, QTableWidgetItem(rec["mandi"]))
            self.mandi_table.setItem(row, 2, QTableWidgetItem(rec["commodity"]))
            self.mandi_table.setItem(row, 3, QTableWidgetItem(str(rec["min_price"])))
            self.mandi_table.setItem(row, 4, QTableWidgetItem(str(rec["max_price"])))
            self.mandi_table.setItem(row, 5, QTableWidgetItem(str(rec["modal_price"])))

    def filter_mandi_table(self):
        search_text = self.mandi_search.text().lower()
        district = self.combo_district.currentText()
        records = get_mandi_prices_from_csv(district)
        filtered = [r for r in records if search_text in r["mandi"].lower() or search_text in r["commodity"].lower()]
        self.populate_mandi_table(filtered)

    def export_advisory_report(self):
        district = self.combo_district.currentText()
        month = self.combo_month.currentText()
        land_size = self.spin_land.value()

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Advisory Report", f"AgriSmart_{district}_{month}.txt", "Text Files (*.txt)")
        if file_path:
            m_info = SEASON_RAINFALL_MAP.get(month, {})
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=========================================\n")
                f.write("     AGRISMART PUNJAB ADVISORY REPORT   \n")
                f.write("=========================================\n\n")
                f.write(f"District: {district}\n")
                f.write(f"Sowing Month: {month} ({m_info.get('season')})\n")
                f.write(f"Expected Rainfall: {m_info.get('rainfall_level')}\n")
                f.write(f"Seasonal Risk Factor: {m_info.get('risk')}\n")
                f.write(f"Land Size: {land_size} Acres\n\n")
                f.write("Recommended Crops & Probabilities:\n")
                crops = ENHANCED_DISTRICT_DATA.get(district, [])
                soil = get_soil_data_from_csv(district)
                for c in crops:
                    prob = calculate_seasonal_crop_probability(c['crop'], c['base_probability'], soil, month)
                    f.write(f"- {c['crop']}: {prob}% Success Probability\n")
            QMessageBox.information(self, "Export Successful", f"Report saved to:\n{file_path}")

    def open_login_dialog(self):
        dialog = DualLoginDialog(self, current_lang=self.current_lang)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.logged_in_user = dialog.user_profile
            dist = self.logged_in_user.get("district")
            land = self.logged_in_user.get("land")
            if dist:
                idx = self.combo_district.findText(dist)
                if idx != -1:
                    self.combo_district.setCurrentIndex(idx)
            if land:
                self.spin_land.setValue(float(land))
            self.on_selection_changed()
            self.update_language_texts()

    def handle_logout(self):
        self.logged_in_user = None
        self.update_language_texts()
        QMessageBox.information(self, "Logout", "You have been logged out successfully.")

    def on_language_change(self, index):
        self.current_lang = self.lang_dropdown.itemData(index)
        self.update_language_texts()

    def update_language_texts(self):
        t = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        self.setWindowTitle(t["app_title"])
        self.btn_advisor.setText(t["nav_advisor"])
        self.btn_mandi.setText(t["nav_mandi"])
        self.btn_google_portal.setText(t["nav_portal_link"])

        if self.logged_in_user:
            user_name = self.logged_in_user.get("name", "Farmer")
            self.banner_title.setText(f"{t['banner_welcome']} ({user_name})")
            self.btn_login.setText(f"👤 {user_name}")
            self.btn_logout.setVisible(True)
        else:
            self.banner_title.setText(t["banner_welcome"])
            self.btn_login.setText(t["login_btn"])
            self.btn_logout.setVisible(False)

        self.banner_sub.setText(t["banner_sub"])
        self.lbl_district.setText(t["district_label"])
        self.lbl_month.setText(t["month_label"])
        self.lbl_land.setText(t["land_label"])
        self.btn_calculate.setText(t["calc_btn"])
        self.btn_export.setText(t["export_btn"])
        self.mandi_search.setPlaceholderText(t["mandi_search_ph"])
        self.btn_logout.setText(t["logout_btn"])

def main():
    app = QApplication(sys.argv)
    lang_dialog = LanguageSelectionDialog()
    if lang_dialog.exec() == QDialog.DialogCode.Accepted:
        selected_lang = lang_dialog.selected_language
    else:
        sys.exit(0)

    login_dialog = DualLoginDialog(current_lang=selected_lang)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        user_profile = login_dialog.user_profile
    else:
        sys.exit(0)

    main_win = MainApp(initial_lang=selected_lang, initial_user=user_profile)
    main_win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
