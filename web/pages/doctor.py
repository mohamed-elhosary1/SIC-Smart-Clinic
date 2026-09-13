import reflex as rx
from web import styles
from web.state import State
from web.components.navbar import navbar
from web.components.status_badge import priority_badge, status_badge
from web.components.empty_state import empty_state
from web.dialogs.history_dialog import history_dialog


def ecg_waveform_svg() -> rx.Component:
    """Render inline SVG ECG lead rhythm strip matching Stitch doctor portal."""
    return rx.html("""
    <svg class="w-full h-8 text-primary" fill="none" preserveAspectRatio="none" viewBox="0 0 500 40" style="color: #1e3a8a;">
      <path d="M0,20 L60,20 L70,20 L75,12 L80,26 L85,6 L90,32 L95,20 L105,20 L115,16 L125,20 L180,20 L190,20 L195,12 L200,26 L205,6 L210,32 L215,20 L225,20 L235,16 L245,20 L300,20 L310,20 L315,12 L320,26 L325,6 L330,32 L335,20 L345,20 L355,16 L365,20 L420,20 L430,20 L435,12 L440,26 L445,6 L450,32 L455,20 L465,20 L475,16 L485,20 L500,20" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
    </svg>
    """)


def doctor_queue_row(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(priority_badge(item["priority_str"])),
        rx.table.cell(
            rx.hstack(
                rx.avatar(fallback=item["patient_initials"], size="1", radius="full", color_scheme="indigo"),
                rx.vstack(
                    rx.text(item["patient_name"], font_size="13px", font_weight="600"),
                    rx.text(item["patient_id"], font_size="11px", color=styles.ON_SURFACE_VARIANT),
                    spacing="0",
                    align_items="start",
                ),
                align_items="center",
                spacing="2",
            )
        ),
        rx.table.cell(rx.text(item["slot_str"], font_size="12px", font_weight="600")),
        rx.table.cell(rx.text(item["case_type"], font_size="13px")),
        rx.table.cell(status_badge(item["status_str"])),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    item["status"] == "pending",
                    rx.button("Call In", size="1", color_scheme="blue", variant="surface", on_click=lambda: State.start_consultation(item["index"])),
                ),
                rx.cond(
                    item["status"] == "in_progress",
                    rx.button("Complete", size="1", color_scheme="green", variant="surface", on_click=lambda: State.complete_consultation(item["index"])),
                ),
                rx.button("History", size="1", variant="ghost", on_click=lambda: State.inspect_patient_history(item["patient_id"])),
                spacing="2",
            )
        ),
    )


def doctor_page() -> rx.Component:
    """Render Dedicated Doctor Portal matching Stitch reference."""
    active = State.doctor_active_consultation

    return rx.box(
        navbar(breadcrumb="Clinical Portal"),
        rx.box(
            rx.vstack(
                # Doctor Header & Availability Bar
                rx.box(
                    rx.hstack(
                        rx.hstack(
                            rx.avatar(
                                src="/doctor_hero.png",
                                fallback="DR",
                                size="4",
                                radius="medium",
                                color_scheme="indigo",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.hstack(rx.text("Good morning, ", font_size="16px", font_weight="400", color=styles.ON_SURFACE_VARIANT), rx.text(State.doctor_profile["name"], font_size="16px", font_weight="400", color=styles.ON_SURFACE_VARIANT), spacing="0"),
                                    rx.badge("MD, CLINICIAN", size="1", color_scheme="indigo", variant="surface"),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.hstack(
                                    rx.text("Specialty: ", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                                    rx.text(State.doctor_profile["specialty"], font_size="13px", color=styles.ON_SURFACE_VARIANT),
                                    rx.text(" • Clinic Station 1", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                                    spacing="0",
                                ),
                                spacing="0",
                                align_items="start",
                            ),
                            align_items="center",
                            spacing="3",
                        ),
                        rx.spacer(),
                        rx.hstack(
                            # Doctor Availability Toggle Button
                            rx.button(
                                rx.hstack(
                                    rx.box(
                                        width="8px",
                                        height="8px",
                                        border_radius="9999px",
                                        background_color=rx.cond(State.doctor_profile["availability"], styles.COMPLETED, styles.ERROR),
                                    ),
                                    rx.text(rx.cond(State.doctor_profile["availability"], "AVAILABLE FOR CONSULT", "BUSY / IN PROCEDURE")),
                                    align_items="center",
                                    spacing="2",
                                ),
                                variant="surface",
                                color_scheme=rx.cond(State.doctor_profile["availability"], "green", "red"),
                                size="2",
                                cursor="pointer",
                                on_click=lambda: State.toggle_doctor_availability(State.doctor_profile["person_id"]),
                            ),
                            align_items="center",
                            spacing="3",
                        ),
                        align_items="center",
                        width="100%",
                        flex_wrap="wrap",
                    ),
                    padding="20px 24px",
                    background_color=styles.SURFACE_CONTAINER_LOWEST,
                    border=f"1px solid {styles.BORDER}",
                    border_radius="16px",
                    box_shadow="0 1px 3px rgba(15, 23, 42, 0.04)",
                    width="100%",
                ),
                # Clinician KPI Strip (4 Cards)
                rx.grid(
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("TODAY'S PATIENTS", font_size="11px", font_weight="600", color=styles.OUTLINE, letter_spacing="0.05em"),
                                rx.spacer(),
                                rx.icon("calendar", size=18, color=styles.PRIMARY_CONTAINER),
                                width="100%",
                            ),
                            rx.text(State.kpi_metrics["total_patients"], font_size="28px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                            rx.text("Active patient records", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                            spacing="1",
                        ),
                        padding="18px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="12px",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("WAITING LOUNGE", font_size="11px", font_weight="600", color=styles.OUTLINE, letter_spacing="0.05em"),
                                rx.spacer(),
                                rx.icon("hourglass", size=18, color=styles.PENDING),
                                width="100%",
                            ),
                            rx.text(State.kpi_metrics["waiting_queue"], font_size="28px", font_weight="700", color=styles.PENDING, font_family=styles.FONT_HEADLINE),
                            rx.text("Awaiting consultation call", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                            spacing="1",
                        ),
                        padding="18px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="12px",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("COMPLETED VISITS", font_size="11px", font_weight="600", color=styles.OUTLINE, letter_spacing="0.05em"),
                                rx.spacer(),
                                rx.icon("circle-check", size=18, color=styles.COMPLETED),
                                width="100%",
                            ),
                            rx.text(State.kpi_metrics["completed_today"], font_size="28px", font_weight="700", color=styles.COMPLETED, font_family=styles.FONT_HEADLINE),
                            rx.text("Concluded consultations", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                            spacing="1",
                        ),
                        padding="18px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="12px",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text("TODAY'S REVENUE", font_size="11px", font_weight="600", color=styles.OUTLINE, letter_spacing="0.05em"),
                                rx.spacer(),
                                rx.icon("credit-card", size=18, color=styles.SECONDARY_TEAL),
                                width="100%",
                            ),
                            rx.text(State.kpi_metrics["revenue_today_str"], font_size="28px", font_weight="700", color=styles.PRIMARY_CONTAINER, font_family=styles.FONT_HEADLINE),
                            rx.text("Total clinic billing", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                            spacing="1",
                        ),
                        padding="18px",
                        background_color=styles.SURFACE_CONTAINER_LOWEST,
                        border=f"1px solid {styles.BORDER}",
                        border_radius="12px",
                        width="100%",
                    ),
                    columns={"initial": "1", "sm": "2", "md": "4"},
                    spacing="4",
                    width="100%",
                ),
                # Active Examination Bay / Consultation Panel (Stitch Screen 9)
                rx.box(
                    rx.vstack(
                        # Panel Ribbon
                        rx.box(
                            rx.hstack(
                                rx.hstack(
                                    rx.icon("activity", size=18, color=styles.SECONDARY_CONTAINER),
                                    rx.text("ACTIVE EXAMINATION BAY 01", font_size="12px", font_weight="700", color=styles.ON_PRIMARY, letter_spacing="0.05em"),
                                    align_items="center",
                                    spacing="2",
                                ),
                                rx.spacer(),
                                rx.hstack(
                                    rx.badge("ECG SYNCHRONIZED", size="1", color_scheme="teal", variant="solid"),
                                    align_items="center",
                                    spacing="2",
                                ),
                                align_items="center",
                                width="100%",
                            ),
                            padding="12px 24px",
                            background_color=styles.PRIMARY_CONTAINER,
                            width="100%",
                        ),
                        # Patient Identity & Action Deck
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.avatar(src="/patient_hero.jpg", fallback="PT", size="3", radius="full", color_scheme="indigo"),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.text(
                                                active["patient_name"],
                                                font_size="20px",
                                                font_weight="700",
                                                color=styles.ON_SURFACE,
                                                font_family=styles.FONT_HEADLINE,
                                            ),
                                            rx.badge(active["patient_id"], size="1", color_scheme="gray"),
                                            priority_badge(active["priority_str"]),
                                            align_items="center",
                                            spacing="2",
                                        ),
                                        rx.hstack(
                                            rx.hstack(rx.text("Scheduled Slot: ", font_size="13px", color=styles.ON_SURFACE_VARIANT), rx.text(active["slot_str"], font_size="13px", color=styles.ON_SURFACE_VARIANT), spacing="0"),
                                            rx.text("•", color=styles.OUTLINE_VARIANT),
                                            rx.hstack(rx.text("Complaint: ", font_size="13px", font_weight="600", color=styles.PRIMARY_CONTAINER), rx.text(active["case_type"], font_size="13px", font_weight="600", color=styles.PRIMARY_CONTAINER), spacing="0"),
                                            align_items="center",
                                            spacing="2",
                                        ),
                                        spacing="0",
                                        align_items="start",
                                    ),
                                    align_items="center",
                                    spacing="3",
                                    width="100%",
                                ),
                                # Clinical Actions Deck
                                rx.grid(
                                    rx.button(
                                        rx.hstack(rx.icon("circle-play", size=18), rx.text("Start Consultation"), align_items="center", spacing="1"),
                                        style=styles.BTN_TEAL,
                                        size="3",
                                        on_click=lambda: State.start_consultation(active["index"]),
                                    ),
                                    rx.button(
                                        rx.hstack(rx.icon("circle-check", size=18), rx.text("Complete Visit"), align_items="center", spacing="1"),
                                        style=styles.BTN_PRIMARY,
                                        size="3",
                                        on_click=lambda: State.complete_consultation(active["index"]),
                                    ),
                                    rx.button(
                                        rx.hstack(rx.icon("file-text", size=18), rx.text("Full Medical History"), align_items="center", spacing="1"),
                                        style=styles.BTN_SECONDARY,
                                        size="3",
                                        on_click=lambda: State.inspect_patient_history(active["patient_id"]),
                                    ),
                                    rx.button(
                                        rx.hstack(rx.icon("circle-x", size=18), rx.text("Cancel Slot"), align_items="center", spacing="1"),
                                        style=styles.BTN_DESTRUCTIVE,
                                        size="3",
                                        on_click=lambda: State.cancel_appointment(active["index"]),
                                    ),
                                    columns={"initial": "2", "md": "4"},
                                    spacing="3",
                                    width="100%",
                                    margin_top="14px",
                                ),
                                # Synchronized Vitals & ECG Waveform Strip
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.text("SYNCHRONIZED VITALS STREAM (TELEMETRY)", font_size="11px", font_weight="700", color=styles.OUTLINE, letter_spacing="0.05em"),
                                            rx.spacer(),
                                            rx.badge("Live Monitor: Connected", size="1", color_scheme="green", variant="surface"),
                                            align_items="center",
                                            width="100%",
                                        ),
                                        rx.grid(
                                            rx.box(
                                                rx.text("BP (Systemic)", font_size="11px", color=styles.OUTLINE),
                                                rx.text("142/88", font_size="16px", font_weight="700", color=styles.ERROR),
                                                rx.text("mmHg (Stage 1)", font_size="11px", color=styles.ON_SURFACE_VARIANT),
                                                padding="8px",
                                                background_color=styles.SURFACE_CONTAINER_LOWEST,
                                                border_radius="8px",
                                            ),
                                            rx.box(
                                                rx.text("Heart Rate", font_size="11px", color=styles.OUTLINE),
                                                rx.text("82 bpm", font_size="16px", font_weight="700", color=styles.ON_SURFACE),
                                                rx.text("Sinus Regular", font_size="11px", color=styles.SECONDARY_TEAL),
                                                padding="8px",
                                                background_color=styles.SURFACE_CONTAINER_LOWEST,
                                                border_radius="8px",
                                            ),
                                            rx.box(
                                                rx.text("Core Temp", font_size="11px", color=styles.OUTLINE),
                                                rx.text("98.6°F", font_size="16px", font_weight="700", color=styles.ON_SURFACE),
                                                rx.text("37.0°C Normal", font_size="11px", color=styles.ON_SURFACE_VARIANT),
                                                padding="8px",
                                                background_color=styles.SURFACE_CONTAINER_LOWEST,
                                                border_radius="8px",
                                            ),
                                            rx.box(
                                                rx.text("SpO2 Pulse-Ox", font_size="11px", color=styles.OUTLINE),
                                                rx.text("99%", font_size="16px", font_weight="700", color=styles.SECONDARY_TEAL),
                                                rx.text("Room Air", font_size="11px", color=styles.ON_SURFACE_VARIANT),
                                                padding="8px",
                                                background_color=styles.SURFACE_CONTAINER_LOWEST,
                                                border_radius="8px",
                                            ),
                                            columns="4",
                                            spacing="3",
                                            width="100%",
                                            margin_top="8px",
                                        ),
                                        ecg_waveform_svg(),
                                        spacing="2",
                                        width="100%",
                                    ),
                                    padding="16px",
                                    background_color=styles.SURFACE_CONTAINER_LOW,
                                    border_radius="12px",
                                    width="100%",
                                    margin_top="14px",
                                ),
                                width="100%",
                                padding="24px",
                                spacing="0",
                            ),
                            width="100%",
                        ),
                        spacing="0",
                        width="100%",
                    ),
                    background_color=styles.SURFACE_CONTAINER_LOWEST,
                    border=f"1px solid {styles.BORDER}",
                    border_radius="16px",
                    overflow="hidden",
                    box_shadow="0 4px 6px -1px rgba(15, 23, 42, 0.05)",
                    width="100%",
                ),
                # Dedicated Doctor Queue Table
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("My Clinical Queue — ", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                    rx.text(State.doctor_profile["name"], font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                                    spacing="0",
                                ),
                                rx.text("Prioritized waiting patients assigned to your examination bay", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                                spacing="0",
                                align_items="start",
                            ),
                            rx.spacer(),
                            rx.segmented_control.root(
                                rx.segmented_control.item("My Patients", value="my"),
                                rx.segmented_control.item("All Patients", value="all"),
                                value=State.doctor_queue_filter,
                                on_change=State.set_doctor_queue_filter,
                                size="2",
                            ),
                            align_items="center",
                            width="100%",
                            padding="18px 24px",
                            border_bottom=f"1px solid {styles.BORDER}",
                        ),
                        rx.box(
                            rx.cond(
                                State.doctor_queue.length() > 0,
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Priority"),
                                            rx.table.column_header_cell("Patient"),
                                            rx.table.column_header_cell("Time Slot (30m)"),
                                            rx.table.column_header_cell("Case Type"),
                                            rx.table.column_header_cell("Status"),
                                            rx.table.column_header_cell("Actions"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(State.doctor_queue, doctor_queue_row),
                                    ),
                                    width="100%",
                                    variant="surface",
                                ),
                                empty_state("calendar-check", "No patients in your queue", "All scheduled consultations are currently up to date."),
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
                padding=["16px", "24px", "32px"],
                max_width="1400px",
                margin="0 auto",
            ),
            width="100%",
            min_height="100vh",
            background_color=styles.SURFACE,
        ),
        history_dialog(),
        width="100%",
        min_height="100vh",
        background_color=styles.SURFACE,
        on_mount=State.on_load,
    )
