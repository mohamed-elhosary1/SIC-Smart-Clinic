import sys
from pathlib import Path
import reflex as rx

_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from smart_clinic.web import styles
from smart_clinic.web.pages.login import login_page
from smart_clinic.web.pages.staff import staff_page
from smart_clinic.web.pages.doctor import doctor_page
from smart_clinic.web.pages.patient import patient_page

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap",
        "/styles.css",
    ],
    head_components=[
        rx.html("<title>Smart Clinic Queue System - Samsung Innovation Campus</title>"),
    ],
)

app.add_page(login_page, route="/", title="Login | Smart Clinic")
app.add_page(staff_page, route="/staff", title="Staff Administration | Smart Clinic")
app.add_page(doctor_page, route="/doctor", title="Doctor Portal | Smart Clinic")
app.add_page(patient_page, route="/patient", title="Patient Kiosk | Smart Clinic")
