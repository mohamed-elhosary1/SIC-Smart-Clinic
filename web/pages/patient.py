import reflex as rx
from web import styles
from web.state import State
from web.components.navbar import navbar
from web.components.status_badge import status_badge
from web.components.empty_state import empty_state


def gauge_countdown_svg(mins: rx.Var[int] | int) -> rx.Component:
    """Render circular gauge ring countdown matching Stitch patient portal."""
    return rx.html("""
    <div style="position: relative; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center;">
      <svg style="width: 100%; height: 100%; transform: rotate(-90deg);" viewBox="0 0 36 36">
        <path style="color: #dce9ff;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="3.5"/>
        <path style="color: #0d9488;" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-dasharray="75, 100" stroke-linecap="round" stroke-width="3.5"/>
      </svg>
      <span style="position: absolute; font-size: 13px; font-weight: 700; color: #1e3a8a; font-family: Inter, sans-serif;">~15m</span>
    </div>
    """)


def patient_appt_row(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.hstack(rx.text("Dr. ", font_size="13px", font_weight="600"), rx.text(item["doctor_name"], font_size="13px", font_weight="600"), spacing="0")),
        rx.table.cell(rx.text(item["doctor_specialty"], font_size="12px", color=styles.ON_SURFACE_VARIANT)),
        rx.table.cell(rx.text(item["slot_str"], font_size="12px", font_weight="600")),
        rx.table.cell(rx.text(item["case_type"], font_size="13px")),
        rx.table.cell(status_badge(item["status_str"])),
        rx.table.cell(rx.text(item["fee_str"], font_size="13px", font_weight="700", color=styles.PRIMARY_CONTAINER)),
    )


def patient_page() -> rx.Component:
    """Render Patient Kiosk Experience matching Stitch patient_portal_live_queue/code.html."""
    ticket = State.patient_queue_ticket
    profile = State.patient_profile

    return rx.box(
        navbar(breadcrumb="Patient Kiosk Tracker"),
        # Patient Header Context Bar
        rx.box(
            rx.hstack(
                rx.avatar(src="/patient_hero.jpg", fallback="PT", size="3", radius="full", color_scheme="teal"),
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.text("Welcome, ", font_size=["18px", "22px"], font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                            rx.text(profile["name"], font_size=["18px", "22px"], font_weight="700", color=styles.PRIMARY_CONTAINER, font_family=styles.FONT_HEADLINE),
                            spacing="1",
                        ),
                        rx.badge(profile["person_id"], size="2", color_scheme="indigo"),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.hstack(
                        rx.icon("circle-check", size=14, color=styles.SECONDARY_TEAL),
                        rx.text("Phone: ", profile["phone"], " • Case: ", profile["case_type"], font_size="13px", color=styles.ON_SURFACE_VARIANT),
                        align_items="center",
                        spacing="1",
                    ),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon("arrow-left", size=16), rx.text("Switch Patient / Logout"), align_items="center", spacing="1"),
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                        on_click=State.logout,
                    ),
                    spacing="2",
                ),
                align_items="center",
                width="100%",
                padding="18px 24px",
                max_width="1200px",
                margin="0 auto",
                flex_wrap="wrap",
            ),
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border_bottom=f"1px solid {styles.BORDER}",
            width="100%",
        ),
        # Main Patient Experience Container
        rx.box(
            rx.vstack(
                # State Simulator Toggle Strip
                rx.hstack(
                    rx.hstack(
                        rx.icon("sliders-horizontal", size=16, color=styles.ON_SURFACE_VARIANT),
                        rx.text("SIMULATE CLINICAL STAGE TRACKER:", font_size="11px", font_weight="700", color=styles.OUTLINE, letter_spacing="0.05em"),
                        align_items="center",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.segmented_control.root(
                        rx.segmented_control.item("1. WAITING IN QUEUE", value="waiting"),
                        rx.segmented_control.item("2. IN CONSULTATION", value="consulting"),
                        rx.segmented_control.item("3. VISIT COMPLETED", value="completed"),
                        value=State.patient_stage_sim,
                        on_change=State.set_patient_stage_sim,
                        size="2",
                    ),
                    align_items="center",
                    width="100%",
                    padding="10px 16px",
                    background_color=styles.SURFACE_CONTAINER_LOW,
                    border_radius="12px",
                ),
                # STAGE 1: WAITING VIEW (Hero Queue Ticket Card)
                rx.cond(
                    State.patient_stage_sim == "waiting",
                    rx.box(
                        rx.vstack(
                            # Top Indicator
                            rx.hstack(
                                rx.hstack(
                                    rx.box(width="8px", height="8px", border_radius="9999px", background_color=styles.PRIMARY_CONTAINER),
                                    rx.text("LIVE TELEMETRY • YOUR QUEUE POSITION", font_size="11px", font_weight="700", color=styles.PRIMARY_CONTAINER, letter_spacing="0.06em"),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.spacer(),
                                rx.badge("ACTIVE IN QUEUE", size="2", color_scheme="amber", variant="surface", font_weight="700"),
                                align_items="center",
                                width="100%",
                            ),
                            # Giant Number & Position Anchor
                            rx.hstack(
                                rx.vstack(
                                    rx.text(
                                        ticket["position_str"],
                                        font_size=["56px", "72px", "88px"],
                                        font_weight="800",
                                        color=styles.PRIMARY_CONTAINER,
                                        font_family=styles.FONT_HEADLINE,
                                        line_height="1",
                                    ),
                                    rx.text("Ticket Reference", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                    spacing="0",
                                    align_items="start",
                                ),
                                rx.vstack(
                                    rx.text(
                                        ticket["queue_headline"],
                                        font_size=["18px", "22px"],
                                        font_weight="700",
                                        color=styles.ON_SURFACE,
                                        font_family=styles.FONT_HEADLINE,
                                    ),
                                    rx.text(
                                        "Please remain in the Clinic Floor A waiting area. A chime and SMS notification will alert you when your doctor is ready.",
                                        font_size="14px",
                                        color=styles.ON_SURFACE_VARIANT,
                                        line_height="1.4",
                                    ),
                                    spacing="1",
                                    align_items="start",
                                    max_width="480px",
                                ),
                                rx.spacer(),
                                # Gauge Ring
                                rx.box(
                                    rx.hstack(
                                        gauge_countdown_svg(15),
                                        rx.vstack(
                                            rx.text("Estimated Call Time", font_size="11px", color=styles.OUTLINE, font_weight="600"),
                                            rx.text(ticket["estimated_call"], font_size="18px", font_weight="700", color=styles.ON_SURFACE),
                                            rx.text("~15 mins remaining", font_size="12px", color=styles.SECONDARY_TEAL, font_weight="500"),
                                            spacing="0",
                                            align_items="start",
                                        ),
                                        align_items="center",
                                        spacing="3",
                                    ),
                                    padding="14px 18px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="12px",
                                ),
                                align_items="center",
                                width="100%",
                                flex_wrap="wrap",
                                spacing="5",
                                padding_y="12px",
                            ),
                            # Telemetry Data Mosaic (4 Cards)
                            rx.grid(
                                rx.box(
                                    rx.text("ASSIGNED DOCTOR", font_size="11px", font_weight="600", color=styles.OUTLINE),
                                    rx.text(ticket["doctor_display"], font_size="15px", font_weight="700", color=styles.ON_SURFACE),
                                    rx.text(ticket["doctor_specialty"], font_size="12px", color=styles.PRIMARY_CONTAINER),
                                    padding="14px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="10px",
                                ),
                                rx.box(
                                    rx.text("CONSULTATION ROOM", font_size="11px", font_weight="600", color=styles.OUTLINE),
                                    rx.text("Clinic Suite 1", font_size="15px", font_weight="700", color=styles.ON_SURFACE),
                                    rx.text("Ground Floor • West Wing", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                    padding="14px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="10px",
                                ),
                                rx.box(
                                    rx.text("SCHEDULED SLOT (30M)", font_size="11px", font_weight="600", color=styles.OUTLINE),
                                    rx.text(ticket["slot_str"], font_size="15px", font_weight="700", color=styles.ON_SURFACE),
                                    rx.text("30-Minute Reserved Window", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                    padding="14px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="10px",
                                ),
                                rx.box(
                                    rx.text("SMS NOTIFICATION", font_size="11px", font_weight="600", color=styles.OUTLINE),
                                    rx.hstack(rx.icon("circle-check", size=14, color=styles.SECONDARY_TEAL), rx.text("SMS Connected", font_size="13px", font_weight="700", color=styles.SECONDARY_TEAL), align_items="center", spacing="1"),
                                    rx.text(profile["phone"], font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                    padding="14px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="10px",
                                ),
                                columns={"initial": "1", "sm": "2", "md": "4"},
                                spacing="3",
                                width="100%",
                            ),
                            # Action Row
                            rx.hstack(
                                rx.button(
                                    rx.hstack(rx.icon("refresh-cw", size=16), rx.text("Refresh Queue"), align_items="center", spacing="1"),
                                    style=styles.BTN_SECONDARY,
                                    size="2",
                                    on_click=State.on_load,
                                ),
                                rx.spacer(),
                                rx.hstack(
                                    rx.icon("radio", size=14, color=styles.SECONDARY_TEAL),
                                    rx.text("Live sync active • Auto-updates with clinic database", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                    align_items="center",
                                    spacing="1",
                                ),
                                align_items="center",
                                width="100%",
                                margin_top="12px",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        padding="28px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="16px",
                        box_shadow="0 4px 6px -1px rgba(15, 23, 42, 0.05)",
                        width="100%",
                    ),
                ),
                # STAGE 2: IN CONSULTATION TEAL BANNER
                rx.cond(
                    State.patient_stage_sim == "consulting",
                    rx.box(
                        rx.hstack(
                            rx.center(
                                rx.icon("stethoscope", size=36, color=styles.ON_PRIMARY),
                                width="64px",
                                height="64px",
                                border_radius="16px",
                                background_color="rgba(255,255,255,0.15)",
                            ),
                            rx.vstack(
                                rx.badge("STAGE 2 • LIVE SESSION", size="1", color_scheme="teal", variant="solid"),
                                rx.text(
                                    "YOU ARE CURRENTLY BEING SEEN",
                                    font_size="24px",
                                    font_weight="800",
                                    color=styles.ON_PRIMARY,
                                    font_family=styles.FONT_HEADLINE,
                                ),
                                rx.hstack(
                                    rx.text("Please proceed inside Clinic Suite 1. Dr. ", font_size="14px", color=styles.ON_PRIMARY, opacity="0.9"),
                                    rx.text(ticket["doctor_name"], font_size="14px", font_weight="700", color=styles.ON_PRIMARY),
                                    rx.text(" has commenced your consultation session.", font_size="14px", color=styles.ON_PRIMARY, opacity="0.9"),
                                    spacing="0",
                                ),
                                spacing="1",
                                align_items="start",
                            ),
                            rx.spacer(),
                            rx.box(
                                rx.vstack(
                                    rx.text("SESSION ELAPSED", font_size="11px", font_weight="700", color=styles.ON_PRIMARY, opacity="0.8"),
                                    rx.text("08:45 min", font_size="22px", font_weight="800", color=styles.ON_PRIMARY, font_family="monospace"),
                                    rx.text("Recording vitals & medical note", font_size="12px", color=styles.ON_PRIMARY, opacity="0.8"),
                                    spacing="0",
                                    align_items="end",
                                ),
                                padding="14px 18px",
                                background_color="rgba(255,255,255,0.12)",
                                border_radius="12px",
                            ),
                            align_items="center",
                            width="100%",
                            flex_wrap="wrap",
                            spacing="4",
                        ),
                        padding="28px",
                        background_color=styles.SECONDARY_TEAL,
                        border_radius="16px",
                        box_shadow="0 10px 15px -3px rgba(13, 148, 136, 0.2)",
                        width="100%",
                    ),
                ),
                # STAGE 3: VISIT COMPLETED SUMMARY CARD
                rx.cond(
                    State.patient_stage_sim == "completed",
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.center(
                                    rx.icon("circle-check", size=32, color=styles.COMPLETED),
                                    width="54px",
                                    height="54px",
                                    border_radius="12px",
                                    background_color=styles.COMPLETED_CONTAINER,
                                ),
                                rx.vstack(
                                    rx.text("Consultation Concluded & Discharged", font_size="20px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                    rx.text("Your medical consultation has completed. Diagnosis and billing receipt recorded.", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                                    spacing="0",
                                    align_items="start",
                                ),
                                rx.spacer(),
                                rx.badge("VISIT CONCLUDED", size="2", color_scheme="green", variant="surface", font_weight="700"),
                                align_items="center",
                                width="100%",
                            ),
                            rx.divider(color=styles.BORDER, margin_y="8px"),
                            rx.grid(
                                rx.box(
                                    rx.text("ATTENDING PHYSICIAN", font_size="11px", color=styles.OUTLINE, font_weight="600"),
                                    rx.hstack(rx.text("Dr. ", font_size="14px", font_weight="700", color=styles.ON_SURFACE), rx.text(ticket["doctor_name"], font_size="14px", font_weight="700", color=styles.ON_SURFACE), spacing="0"),
                                    padding="10px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="8px",
                                ),
                                rx.box(
                                    rx.text("DIAGNOSTIC STATUS", font_size="11px", color=styles.OUTLINE, font_weight="600"),
                                    rx.text("Routine Ambulatory Evaluation", font_size="14px", font_weight="700", color=styles.ON_SURFACE),
                                    padding="10px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="8px",
                                ),
                                rx.box(
                                    rx.text("BILLED RECEPTION FEE", font_size="11px", color=styles.OUTLINE, font_weight="600"),
                                    rx.text("$100.00 (Standard)", font_size="14px", font_weight="700", color=styles.PRIMARY_CONTAINER),
                                    padding="10px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="8px",
                                ),
                                columns="3",
                                spacing="3",
                                width="100%",
                            ),
                            spacing="3",
                            width="100%",
                        ),
                        padding="24px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="16px",
                        box_shadow="0 2px 4px rgba(0,0,0,0.03)",
                        width="100%",
                    ),
                ),
                # My Scheduled Appointments Table
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("My Scheduled Appointments", font_size="17px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                rx.text("All 30-minute reservation slots for this patient", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                                spacing="0",
                                align_items="start",
                            ),
                            align_items="center",
                            width="100%",
                            padding="16px 20px",
                            border_bottom=f"1px solid {styles.BORDER}",
                        ),
                        rx.box(
                            rx.cond(
                                State.patient_appointments.length() > 0,
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Doctor"),
                                            rx.table.column_header_cell("Specialty"),
                                            rx.table.column_header_cell("Reserved Slot Window"),
                                            rx.table.column_header_cell("Case Type"),
                                            rx.table.column_header_cell("Status"),
                                            rx.table.column_header_cell("Billed Fee"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(State.patient_appointments, patient_appt_row),
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                empty_state("calendar", "No scheduled appointments", "You currently have no active appointment bookings."),
                            ),
                            padding="12px",
                            overflow_x="auto",
                            width="100%",
                        ),
                        spacing="0",
                        width="100%",
                    ),
                    background_color=styles.SURFACE_CONTAINER_LOWEST,
                    border=f"1px solid {styles.BORDER}",
                    border_radius="16px",
                    box_shadow="0 1px 3px rgba(15, 23, 42, 0.04)",
                    width="100%",
                ),
                spacing="5",
                width="100%",
                max_width="1200px",
                margin="0 auto",
                padding=["16px", "24px"],
            ),
            width="100%",
            min_height="calc(100vh - 64px)",
            background_color=styles.SURFACE,
        ),
        width="100%",
        min_height="100vh",
        background_color=styles.SURFACE,
        on_mount=State.on_load,
    )
