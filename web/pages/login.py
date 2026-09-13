import reflex as rx
from web import styles
from web.state import State
from web.components.navbar import clinic_emblem_logo


# =====================================================================
# CSS ANIMATIONS (injected via rx.html)
# =====================================================================

LANDING_CSS = """
<style>
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50%      { transform: scale(1.04); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes floatBadge {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-6px); }
}

.landing-hero-title {
    animation: fadeInUp 0.8s ease-out;
}
.landing-hero-subtitle {
    animation: fadeInUp 0.8s ease-out 0.15s both;
}
.landing-card-left {
    animation: slideInLeft 0.7s ease-out 0.3s both;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.landing-card-left:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.15);
}
.landing-card-right {
    animation: slideInRight 0.7s ease-out 0.3s both;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.landing-card-right:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.15);
}
.landing-badge {
    animation: floatBadge 3s ease-in-out infinite;
}
.form-section {
    animation: fadeInUp 0.5s ease-out;
}
.btn-glow:hover {
    box-shadow: 0 0 20px rgba(30, 58, 138, 0.3);
}
.btn-glow-teal:hover {
    box-shadow: 0 0 20px rgba(13, 148, 136, 0.3);
}
.back-btn {
    animation: fadeIn 0.3s ease-out;
    transition: all 0.2s ease;
}
.back-btn:hover {
    transform: translateX(-4px);
}
.card-image {
    transition: transform 0.4s ease;
}
.card-image:hover {
    transform: scale(1.05);
}
</style>
"""


# =====================================================================
# LANDING HERO CHOOSER (Patient vs Admin/Doctor)
# =====================================================================

def _hero_chooser() -> rx.Component:
    """Two large clickable cards with images: Patient vs Admin/Doctor."""
    return rx.vstack(
        # Branding Header
        rx.vstack(
            rx.image(
                src="/clinic_logo.png",
                width="80px",
                height="80px",
                alt="Smart Clinic Logo",
                border_radius="16px",
            ),
            rx.text(
                "SMART CLINIC",
                font_size=["28px", "36px"],
                font_weight="800",
                color=styles.PRIMARY_CONTAINER,
                font_family=styles.FONT_HEADLINE,
                letter_spacing="-0.03em",
                line_height="1.1",
                text_align="center",
                class_name="landing-hero-title",
            ),
            rx.text(
                "Queue Management System",
                font_size=["16px", "20px"],
                font_weight="600",
                color=styles.ON_SURFACE,
                font_family=styles.FONT_HEADLINE,
                text_align="center",
                class_name="landing-hero-title",
            ),
            rx.hstack(
                rx.badge(
                    "Samsung Innovation Campus",
                    size="2",
                    color_scheme="indigo",
                    variant="surface",
                    font_weight="600",
                    class_name="landing-badge",
                ),
                rx.badge(
                    "Intelligent Healthcare Flow",
                    size="2",
                    color_scheme="teal",
                    variant="surface",
                    font_weight="600",
                    class_name="landing-badge",
                ),
                spacing="2",
                justify="center",
            ),
            align_items="center",
            spacing="2",
            margin_bottom="40px",
            class_name="landing-hero-subtitle",
        ),
        # Selection prompt
        rx.text(
            "How would you like to continue?",
            font_size="17px",
            font_weight="500",
            color=styles.ON_SURFACE_VARIANT,
            font_family=styles.FONT_BODY,
            text_align="center",
            margin_bottom="20px",
            class_name="landing-hero-subtitle",
        ),
        # Two Portal Cards
        rx.grid(
            # PATIENT Card
            rx.box(
                rx.vstack(
                    # Image section
                    rx.box(
                        rx.image(
                            src="/patient_hero.jpg",
                            width="100%",
                            height="200px",
                            object_fit="cover",
                            alt="Patient Portal",
                            class_name="card-image",
                        ),
                        width="100%",
                        height="200px",
                        overflow="hidden",
                        border_radius="12px 12px 0 0",
                    ),
                    # Content
                    rx.vstack(
                        rx.hstack(
                            rx.center(
                                rx.icon("heart-pulse", size=24, color=styles.SECONDARY_TEAL),
                                width="44px",
                                height="44px",
                                border_radius="12px",
                                background_color=styles.SURFACE_CONTAINER,
                            ),
                            rx.vstack(
                                rx.text(
                                    "Patient Portal",
                                    font_size="20px",
                                    font_weight="700",
                                    color=styles.ON_SURFACE,
                                    font_family=styles.FONT_HEADLINE,
                                ),
                                rx.text(
                                    "Track your queue & appointments",
                                    font_size="13px",
                                    color=styles.ON_SURFACE_VARIANT,
                                ),
                                spacing="0",
                                align_items="start",
                            ),
                            spacing="3",
                            align_items="center",
                        ),
                        rx.text(
                            "View your live queue position, appointment schedule, and estimated wait time. No password required.",
                            font_size="14px",
                            color=styles.ON_SURFACE_VARIANT,
                            line_height="1.5",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-right", size=18),
                                rx.text("Enter as Patient", font_weight="600"),
                                spacing="2",
                                align_items="center",
                            ),
                            style=styles.BTN_TEAL,
                            width="100%",
                            size="3",
                            class_name="btn-glow-teal",
                            on_click=State.set_landing_mode("patient"),
                        ),
                        padding="20px",
                        spacing="4",
                        width="100%",
                    ),
                    spacing="0",
                    width="100%",
                ),
                background_color=styles.SURFACE_CONTAINER_LOWEST,
                border=f"1px solid {styles.BORDER}",
                border_radius="16px",
                overflow="hidden",
                cursor="pointer",
                class_name="landing-card-left",
                on_click=State.set_landing_mode("patient"),
            ),
            # ADMIN / DOCTOR Card
            rx.box(
                rx.vstack(
                    # Image section
                    rx.box(
                        rx.image(
                            src="/doctor_hero.png",
                            width="100%",
                            height="200px",
                            object_fit="cover",
                            alt="Admin & Doctor Portal",
                            class_name="card-image",
                        ),
                        width="100%",
                        height="200px",
                        overflow="hidden",
                        border_radius="12px 12px 0 0",
                    ),
                    # Content
                    rx.vstack(
                        rx.hstack(
                            rx.center(
                                rx.icon("shield-check", size=24, color=styles.PRIMARY_CONTAINER),
                                width="44px",
                                height="44px",
                                border_radius="12px",
                                background_color=styles.SURFACE_CONTAINER,
                            ),
                            rx.vstack(
                                rx.text(
                                    "Admin / Doctor",
                                    font_size="20px",
                                    font_weight="700",
                                    color=styles.ON_SURFACE,
                                    font_family=styles.FONT_HEADLINE,
                                ),
                                rx.text(
                                    "Manage clinic & consultations",
                                    font_size="13px",
                                    color=styles.ON_SURFACE_VARIANT,
                                ),
                                spacing="0",
                                align_items="start",
                            ),
                            spacing="3",
                            align_items="center",
                        ),
                        rx.text(
                            "Access the staff dashboard, queue management, patient registration, doctor portal, and administrative tools.",
                            font_size="14px",
                            color=styles.ON_SURFACE_VARIANT,
                            line_height="1.5",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-right", size=18),
                                rx.text("Sign In as Staff / Doctor", font_weight="600"),
                                spacing="2",
                                align_items="center",
                            ),
                            style=styles.BTN_PRIMARY,
                            width="100%",
                            size="3",
                            class_name="btn-glow",
                            on_click=State.set_landing_mode("admin"),
                        ),
                        padding="20px",
                        spacing="4",
                        width="100%",
                    ),
                    spacing="0",
                    width="100%",
                ),
                background_color=styles.SURFACE_CONTAINER_LOWEST,
                border=f"1px solid {styles.BORDER}",
                border_radius="16px",
                overflow="hidden",
                cursor="pointer",
                class_name="landing-card-right",
                on_click=State.set_landing_mode("admin"),
            ),
            columns={"initial": "1", "md": "2"},
            spacing="6",
            width="100%",
            max_width="900px",
        ),
        # Footer
        rx.text(
            "© 2025 Smart Clinic • Samsung Innovation Campus Project",
            font_size="12px",
            color=styles.OUTLINE,
            margin_top="32px",
            text_align="center",
        ),
        align_items="center",
        width="100%",
        max_width="960px",
        padding="24px",
    )


# =====================================================================
# PATIENT LOGIN FORM
# =====================================================================

def _patient_form() -> rx.Component:
    """Patient kiosk ID lookup form with back button."""
    return rx.vstack(
        # Back button
        rx.box(
            rx.hstack(
                rx.icon("arrow-left", size=18, color=styles.ON_SURFACE_VARIANT),
                rx.text("Back to Home", font_size="14px", font_weight="500", color=styles.ON_SURFACE_VARIANT),
                spacing="2",
                align_items="center",
            ),
            cursor="pointer",
            on_click=State.go_back_to_landing,
            class_name="back-btn",
            padding="8px 12px",
            border_radius="8px",
            _hover={"background_color": styles.SURFACE_CONTAINER},
            margin_bottom="16px",
        ),
        # Patient form card
        rx.box(
            rx.vstack(
                # Header with image
                rx.box(
                    rx.image(
                        src="/patient_hero.jpg",
                        width="100%",
                        height="160px",
                        object_fit="cover",
                        alt="Patient Portal",
                    ),
                    width="100%",
                    height="160px",
                    overflow="hidden",
                    border_radius="16px 16px 0 0",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon("heart-pulse", size=22, color=styles.SECONDARY_TEAL),
                            width="40px",
                            height="40px",
                            border_radius="10px",
                            background_color=styles.SURFACE_CONTAINER,
                        ),
                        rx.vstack(
                            rx.text(
                                "Patient Self-Service Kiosk",
                                font_size="18px",
                                font_weight="700",
                                color=styles.ON_SURFACE,
                                font_family=styles.FONT_HEADLINE,
                            ),
                            rx.text(
                                "Enter your Patient ID to view your queue position",
                                font_size="13px",
                                color=styles.ON_SURFACE_VARIANT,
                            ),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                        align_items="center",
                    ),
                    rx.vstack(
                        rx.text("Your Patient ID", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            placeholder="e.g. patient-101",
                            value=State.patient_lookup_input,
                            on_change=State.set_patient_lookup,
                            width="100%",
                            size="3",
                        ),
                        rx.text(
                            "No password required. Enter your ID issued at reception.",
                            font_size="12px",
                            color=styles.ON_SURFACE_VARIANT,
                        ),
                        width="100%",
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("search", size=18),
                            rx.text("Track My Queue & Appointments", font_weight="600"),
                            spacing="2",
                            align_items="center",
                        ),
                        style=styles.BTN_TEAL,
                        width="100%",
                        size="3",
                        class_name="btn-glow-teal",
                        on_click=State.login_patient,
                    ),
                    # Quick Demo IDs
                    rx.vstack(
                        rx.text("Quick Demo Patients:", font_size="12px", color=styles.OUTLINE, font_weight="500"),
                        rx.hstack(
                            rx.badge(
                                "⚽ Mo Salah (patient-101)",
                                size="1", color_scheme="blue", variant="surface",
                                cursor="pointer",
                                on_click=State.select_demo_patient("patient-101"),
                            ),
                            rx.badge(
                                "🚑 Haaland - EMG (patient-105)",
                                size="1", color_scheme="red", variant="surface",
                                cursor="pointer",
                                on_click=State.select_demo_patient("patient-105"),
                            ),
                            rx.badge(
                                "⚽ Messi (patient-102)",
                                size="1", color_scheme="teal", variant="surface",
                                cursor="pointer",
                                on_click=State.select_demo_patient("patient-102"),
                            ),
                            rx.badge(
                                "⚽ Ronaldo (patient-103)",
                                size="1", color_scheme="purple", variant="surface",
                                cursor="pointer",
                                on_click=State.select_demo_patient("patient-103"),
                            ),
                            spacing="2",
                            flex_wrap="wrap",
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    padding="24px",
                    spacing="5",
                    width="100%",
                ),
                spacing="0",
                width="100%",
            ),
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="16px",
            overflow="hidden",
            box_shadow="0 10px 30px -8px rgba(15, 23, 42, 0.08)",
            width="100%",
            max_width="480px",
            class_name="form-section",
        ),
        # Error callout
        rx.cond(
            State.login_error_msg != "",
            rx.callout(
                State.login_error_msg,
                icon="circle-alert",
                color_scheme="red",
                size="2",
                width="100%",
                max_width="480px",
                margin_top="12px",
            ),
        ),
        align_items="center",
        width="100%",
        max_width="520px",
        padding="24px",
    )


# =====================================================================
# ADMIN / DOCTOR LOGIN FORM
# =====================================================================

def _admin_form() -> rx.Component:
    """Staff & Doctor credential login form with back button."""
    return rx.vstack(
        # Back button
        rx.box(
            rx.hstack(
                rx.icon("arrow-left", size=18, color=styles.ON_SURFACE_VARIANT),
                rx.text("Back to Home", font_size="14px", font_weight="500", color=styles.ON_SURFACE_VARIANT),
                spacing="2",
                align_items="center",
            ),
            cursor="pointer",
            on_click=State.go_back_to_landing,
            class_name="back-btn",
            padding="8px 12px",
            border_radius="8px",
            _hover={"background_color": styles.SURFACE_CONTAINER},
            margin_bottom="16px",
        ),
        # Admin login card
        rx.box(
            rx.vstack(
                # Header with image
                rx.box(
                    rx.image(
                        src="/doctor_hero.png",
                        width="100%",
                        height="160px",
                        object_fit="cover",
                        object_position="top",
                        alt="Staff & Doctor Portal",
                    ),
                    width="100%",
                    height="160px",
                    overflow="hidden",
                    border_radius="16px 16px 0 0",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon("lock", size=22, color=styles.PRIMARY_CONTAINER),
                            width="40px",
                            height="40px",
                            border_radius="10px",
                            background_color=styles.SURFACE_CONTAINER,
                        ),
                        rx.vstack(
                            rx.text(
                                "Staff & Doctor Portal",
                                font_size="18px",
                                font_weight="700",
                                color=styles.ON_SURFACE,
                                font_family=styles.FONT_HEADLINE,
                            ),
                            rx.text(
                                "Secure administrative & clinical access",
                                font_size="13px",
                                color=styles.ON_SURFACE_VARIANT,
                            ),
                            spacing="0",
                            align_items="start",
                        ),
                        spacing="3",
                        align_items="center",
                    ),
                    rx.vstack(
                        rx.text("Username", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            placeholder="Enter username (e.g. staff, doctor)",
                            value=State.login_username_input,
                            on_change=State.set_login_username,
                            width="100%",
                            size="3",
                        ),
                        width="100%",
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Password", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            type="password",
                            placeholder="••••••••",
                            value=State.login_password_input,
                            on_change=State.set_login_password,
                            width="100%",
                            size="3",
                        ),
                        width="100%",
                        spacing="1",
                        align_items="start",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("log-in", size=18),
                            rx.text("Sign In to Clinic System", font_weight="600"),
                            spacing="2",
                            align_items="center",
                        ),
                        style=styles.BTN_PRIMARY,
                        width="100%",
                        size="3",
                        class_name="btn-glow",
                        on_click=State.login_staff_or_doctor,
                    ),
                    # Quick credentials
                    rx.hstack(
                        rx.text("Demo Credentials:", font_size="12px", color=styles.OUTLINE),
                        rx.badge(
                            "👨‍💼 staff / staff123",
                            size="1", color_scheme="indigo", variant="surface",
                            cursor="pointer",
                            on_click=State.set_staff_demo_creds,
                        ),
                        rx.badge(
                            "🩺 doctor / doc123",
                            size="1", color_scheme="teal", variant="surface",
                            cursor="pointer",
                            on_click=State.set_doctor_demo_creds,
                        ),
                        spacing="2",
                        align_items="center",
                        flex_wrap="wrap",
                    ),
                    padding="24px",
                    spacing="5",
                    width="100%",
                ),
                spacing="0",
                width="100%",
            ),
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="16px",
            overflow="hidden",
            box_shadow="0 10px 30px -8px rgba(15, 23, 42, 0.08)",
            width="100%",
            max_width="480px",
            class_name="form-section",
        ),
        # Error callout
        rx.cond(
            State.login_error_msg != "",
            rx.callout(
                State.login_error_msg,
                icon="circle-alert",
                color_scheme="red",
                size="2",
                width="100%",
                max_width="480px",
                margin_top="12px",
            ),
        ),
        align_items="center",
        width="100%",
        max_width="520px",
        padding="24px",
    )


# =====================================================================
# MAIN LOGIN PAGE
# =====================================================================

def login_page() -> rx.Component:
    """Render animated Landing Page with role selection and login forms."""
    return rx.box(
        rx.html(LANDING_CSS),
        rx.center(
            rx.cond(
                State.landing_mode == "",
                _hero_chooser(),
                rx.cond(
                    State.landing_mode == "patient",
                    _patient_form(),
                    _admin_form(),
                ),
            ),
            width="100%",
            min_height="100vh",
        ),
        width="100%",
        min_height="100vh",
        background=f"linear-gradient(135deg, {styles.SURFACE} 0%, {styles.SURFACE_CONTAINER_LOW} 50%, {styles.SURFACE} 100%)",
        on_mount=State.on_load,
    )
