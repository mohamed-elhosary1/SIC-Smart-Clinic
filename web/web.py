import reflex as rx
from web import styles
from web.pages.login import login_page
from web.pages.staff import staff_page
from web.pages.doctor import doctor_page
from web.pages.patient import patient_page

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
