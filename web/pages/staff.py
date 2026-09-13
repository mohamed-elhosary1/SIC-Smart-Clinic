import reflex as rx
from web import styles
from web.state import State
from web.components.navbar import navbar
from web.components.sidebar import sidebar
from web.components.kpi_card import kpi_card
from web.components.status_badge import priority_badge, status_badge
from web.components.empty_state import empty_state
from web.dialogs.booking_dialog import booking_dialog
from web.dialogs.patient_dialog import patient_dialog
from web.dialogs.doctor_dialog import doctor_dialog
from web.dialogs.history_dialog import history_dialog
from web.dialogs.confirmation_dialog import confirmation_dialog


# =====================================================================
# TABLE ROW COMPONENTS
# =====================================================================

def queue_table_row(item: dict) -> rx.Component:
    return rx.table.row(
        # Priority
        rx.table.cell(priority_badge(item["priority_str"])),
        # Patient
        rx.table.cell(
            rx.hstack(
                rx.avatar(fallback=item["patient_initials"], size="1", radius="full", color_scheme="indigo"),
                rx.vstack(
                    rx.text(item["patient_name"], font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.text(item["patient_id"], font_size="11px", color=styles.ON_SURFACE_VARIANT),
                    spacing="0",
                    align_items="start",
                ),
                align_items="center",
                spacing="2",
            )
        ),
        # Doctor
        rx.table.cell(
            rx.vstack(
                rx.hstack(rx.text("Dr. ", font_size="13px", font_weight="500", color=styles.ON_SURFACE), rx.text(item["doctor_name"], font_size="13px", font_weight="500", color=styles.ON_SURFACE), spacing="0"),
                rx.text(item["doctor_specialty"], font_size="11px", color=styles.ON_SURFACE_VARIANT),
                spacing="0",
                align_items="start",
            )
        ),
        # 30-min Slot Window
        rx.table.cell(
            rx.vstack(
                rx.text(item["slot_str"], font_size="12px", font_weight="600", color=styles.ON_SURFACE),
                rx.text("30-min slot", font_size="11px", color=styles.OUTLINE),
                spacing="0",
                align_items="start",
            )
        ),
        # Case Type
        rx.table.cell(rx.text(item["case_type"], font_size="13px", color=styles.ON_SURFACE)),
        # Status
        rx.table.cell(status_badge(item["status_str"])),
        # Fee
        rx.table.cell(rx.text(item["fee_str"], font_size="13px", font_weight="700", color=styles.PRIMARY_CONTAINER)),
        # Actions
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    item["status"] == "pending",
                    rx.button(
                        "Start",
                        size="1",
                        color_scheme="blue",
                        variant="surface",
                        cursor="pointer",
                        on_click=lambda: State.start_consultation(item["index"]),
                    ),
                ),
                rx.cond(
                    item["status"] == "in_progress",
                    rx.button(
                        "Complete",
                        size="1",
                        color_scheme="green",
                        variant="surface",
                        cursor="pointer",
                        on_click=lambda: State.complete_consultation(item["index"]),
                    ),
                ),
                rx.cond(
                    (item["status"] == "pending") | (item["status"] == "in_progress"),
                    rx.button(
                        "Cancel",
                        size="1",
                        color_scheme="amber",
                        variant="surface",
                        cursor="pointer",
                        on_click=lambda: State.cancel_appointment(item["index"]),
                    ),
                ),
                rx.button(
                    rx.icon("trash-2", size=14, color=styles.ERROR),
                    size="1",
                    variant="ghost",
                    cursor="pointer",
                    on_click=lambda: State.prompt_delete_appointment(item["index"]),
                ),
                spacing="1",
                align_items="center",
            )
        ),
    )


def patient_table_row(item: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.badge(item["person_id"], size="1", color_scheme="gray")),
        rx.table.cell(
            rx.hstack(
                rx.avatar(fallback=item["initials"], size="1", radius="full", color_scheme="indigo"),
                rx.text(item["name"], font_size="13px", font_weight="600"),
                align_items="center",
                spacing="2",
            )
        ),
        rx.table.cell(rx.text(item["phone"], font_size="13px", color=styles.ON_SURFACE)),
        rx.table.cell(rx.text(item["age"], font_size="13px")),
        rx.table.cell(rx.text(item["case_type"], font_size="13px", color=styles.ON_SURFACE_VARIANT)),
        rx.table.cell(priority_badge(item["priority_str"])),
        rx.table.cell(
            rx.button(
                "History",
                size="1",
                variant="surface",
                color_scheme="indigo",
                cursor="pointer",
                on_click=lambda: State.inspect_patient_history(item["person_id"]),
            )
        ),
    )


# =====================================================================
# SUB-VIEWS FOR STAFF PORTAL
# =====================================================================

def view_dashboard() -> rx.Component:
    """Staff Dashboard View matching Stitch staff_dashboard/code.html."""
    return rx.vstack(
        # 5 KPI Cards Row
        rx.grid(
            kpi_card("Total Patients", State.kpi_metrics["total_patients"], "Registered records", "users", trend_text="+12%"),
            kpi_card("Doctors", State.kpi_metrics["total_doctors"], State.kpi_metrics["active_doctors_str"], "stethoscope"),
            kpi_card("Waiting Queue", State.kpi_metrics["waiting_queue"], "Avg wait ~14m", "hourglass", icon_color=styles.PENDING),
            kpi_card("Completed Today", State.kpi_metrics["completed_today"], "Consultations", "circle-check", icon_color=styles.COMPLETED),
            kpi_card("Today's Revenue", State.kpi_metrics["revenue_today_str"], "Today's billing", "credit-card", trend_text="+8.4%"),
            columns={"initial": "1", "sm": "2", "md": "3", "lg": "5"},
            spacing="4",
            width="100%",
        ),
        # Main Dashboard Queue Table & Live Floor Status
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Live Outpatient Queue", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                        rx.text("Real-time room routing and prioritized triage intake feed", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon("calendar-plus", size=16),
                            rx.text("Book Appointment"),
                            align_items="center",
                            spacing="1",
                        ),
                        style=styles.BTN_PRIMARY,
                        size="2",
                        on_click=State.open_booking_modal,
                    ),
                    align_items="center",
                    width="100%",
                    padding="18px 20px",
                    border_bottom=f"1px solid {styles.BORDER}",
                ),
                rx.box(
                    rx.cond(
                        State.filtered_appointments.length() > 0,
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Priority"),
                                    rx.table.column_header_cell("Patient"),
                                    rx.table.column_header_cell("Doctor"),
                                    rx.table.column_header_cell("Slot Window"),
                                    rx.table.column_header_cell("Case Type"),
                                    rx.table.column_header_cell("Status"),
                                    rx.table.column_header_cell("Fee"),
                                    rx.table.column_header_cell("Actions"),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(State.filtered_appointments, queue_table_row),
                            ),
                            width="100%",
                            variant="surface",
                        ),
                        empty_state("calendar-x", "No appointments in queue", "Book a new appointment or adjust your active filters."),
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
            border_radius="12px",
            box_shadow="0 1px 3px rgba(15, 23, 42, 0.04)",
            width="100%",
            margin_top="8px",
        ),
        spacing="5",
        width="100%",
    )


def view_queue() -> rx.Component:
    """Full Queue & Appointments Workstation matching Stitch reference."""
    return rx.vstack(
        # Workstation Toolbar
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.input(
                        placeholder="Search patient, ID, doctor...",
                        value=State.queue_search_query,
                        on_change=State.set_queue_search,
                        width=["100%", "280px"],
                        size="2",
                    ),
                    rx.select(
                        ["All Priorities", "Emergency", "Regular"],
                        value=State.queue_priority_filter,
                        on_change=State.set_queue_priority,
                        size="2",
                    ),
                    rx.select(
                        ["All Statuses", "Waiting", "In Consultation", "Completed", "Cancelled"],
                        value=State.queue_status_filter,
                        on_change=State.set_queue_status,
                        size="2",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(
                            rx.icon("plus", size=16),
                            rx.text("Book Appointment"),
                            align_items="center",
                            spacing="1",
                        ),
                        style=styles.BTN_PRIMARY,
                        size="2",
                        on_click=State.open_booking_modal,
                    ),
                    align_items="center",
                    width="100%",
                    flex_wrap="wrap",
                    spacing="3",
                ),
                spacing="3",
                width="100%",
            ),
            padding="16px 20px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            width="100%",
        ),
        # Appointments Table
        rx.box(
            rx.cond(
                State.filtered_appointments.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Priority"),
                            rx.table.column_header_cell("Patient"),
                            rx.table.column_header_cell("Doctor"),
                            rx.table.column_header_cell("Slot Window (30m)"),
                            rx.table.column_header_cell("Case Type"),
                            rx.table.column_header_cell("Status"),
                            rx.table.column_header_cell("Fee"),
                            rx.table.column_header_cell("Actions"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(State.filtered_appointments, queue_table_row),
                    ),
                    width="100%",
                    variant="surface",
                ),
                empty_state("calendar-x", "No appointments matching filters", "Try changing the search query or priority filters."),
            ),
            padding="12px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            overflow_x="auto",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def view_patients() -> rx.Component:
    """Patient Management View."""
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.input(
                    placeholder="Search by name, ID (e.g. patient-101), phone...",
                    value=State.patient_search_query,
                    on_change=State.set_patient_search,
                    width=["100%", "360px"],
                    size="2",
                ),
                rx.spacer(),
                rx.button(
                    rx.hstack(
                        rx.icon("user-plus", size=16),
                        rx.text("Register New Patient"),
                        align_items="center",
                        spacing="1",
                    ),
                    style=styles.BTN_PRIMARY,
                    size="2",
                    on_click=State.open_patient_modal,
                ),
                align_items="center",
                width="100%",
                flex_wrap="wrap",
                spacing="3",
            ),
            padding="16px 20px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            width="100%",
        ),
        rx.box(
            rx.cond(
                State.filtered_patients.length() > 0,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Patient ID"),
                            rx.table.column_header_cell("Full Name"),
                            rx.table.column_header_cell("Phone (Egyptian 01)"),
                            rx.table.column_header_cell("Age"),
                            rx.table.column_header_cell("Case Type"),
                            rx.table.column_header_cell("Priority"),
                            rx.table.column_header_cell("Medical History"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(State.filtered_patients, patient_table_row),
                    ),
                    width="100%",
                    variant="surface",
                ),
                empty_state("users", "No patients found", "Register a new patient or refine your search query."),
            ),
            padding="12px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            overflow_x="auto",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def doctor_card(doc: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.avatar(src="/doctor_hero.png", fallback=doc["initials"], size="2", radius="full", color_scheme="teal"),
                rx.vstack(
                    rx.hstack(rx.text("Dr. ", font_size="15px", font_weight="700", color=styles.ON_SURFACE), rx.text(doc["name"], font_size="15px", font_weight="700", color=styles.ON_SURFACE), spacing="0"),
                    rx.text(doc["specialty"], font_size="12px", color=styles.ON_SURFACE_VARIANT),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.cond(
                    doc["availability"],
                    rx.badge("AVAILABLE", size="2", color_scheme="green", variant="surface", font_weight="600"),
                    rx.badge("BUSY", size="2", color_scheme="amber", variant="surface", font_weight="600"),
                ),
                align_items="center",
                width="100%",
            ),
            rx.divider(color=styles.BORDER, margin_y="8px"),
            rx.hstack(
                rx.icon("phone", size=14, color=styles.OUTLINE),
                rx.text(doc["phone"], font_size="12px", color=styles.ON_SURFACE),
                rx.spacer(),
                rx.button(
                    rx.cond(doc["availability"], "Mark Busy", "Mark Available"),
                    size="1",
                    variant="soft",
                    color_scheme=rx.cond(doc["availability"], "amber", "green"),
                    cursor="pointer",
                    on_click=lambda: State.toggle_doctor_availability(doc["person_id"]),
                ),
                align_items="center",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        padding="18px",
        background_color=styles.SURFACE_CONTAINER_LOWEST,
        border=f"1px solid {styles.BORDER}",
        border_radius="12px",
        width="100%",
    )


def view_doctors() -> rx.Component:
    """Doctor Roster & Availability View."""
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("Clinical Staff Roster", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                    rx.text("Manage doctors, specialties, and active duty availability", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.hstack(
                        rx.icon("stethoscope", size=16),
                        rx.text("Add Doctor"),
                        align_items="center",
                        spacing="1",
                    ),
                    style=styles.BTN_TEAL,
                    size="2",
                    on_click=State.open_doctor_modal,
                ),
                align_items="center",
                width="100%",
            ),
            padding="16px 20px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            width="100%",
        ),
        rx.grid(
            rx.foreach(State.doctors_list, doctor_card),
            columns={"initial": "1", "sm": "2", "md": "3"},
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def view_reports() -> rx.Component:
    """Daily Report View & TXT Export."""
    return rx.vstack(
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("Daily Clinic Performance Report", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                    rx.text("Unified metrics calculated via functools.reduce and triage closures", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Export Report to TXT"),
                        align_items="center",
                        spacing="1",
                    ),
                    style=styles.BTN_PRIMARY,
                    size="2",
                    on_click=State.export_daily_report,
                ),
                align_items="center",
                width="100%",
            ),
            padding="18px 20px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            width="100%",
        ),
        # Monospace formatted report text
        rx.box(
            rx.text(
                State.daily_report_table_text,
                font_family="monospace",
                font_size="13px",
                white_space="pre",
                color=styles.ON_SURFACE,
                line_height="1.5",
            ),
            padding="24px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            overflow_x="auto",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def view_admin() -> rx.Component:
    """Database & System Administration View."""
    return rx.vstack(
        rx.box(
            rx.vstack(
                rx.text("System & Database Administration", font_size="18px", font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                rx.text("Manage JSON database persistence, self-healing backups, and system state", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                spacing="0",
                align_items="start",
            ),
            padding="18px 20px",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            border=f"1px solid {styles.BORDER}",
            border_radius="12px",
            width="100%",
        ),
        rx.grid(
            # Save Card
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("save", size=24, color=styles.SECONDARY_TEAL),
                        rx.text("Save Database Now", font_size="16px", font_weight="700", color=styles.ON_SURFACE),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.text("Forces immediate serialization of all clinic data to 'clinic_data.json'.", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    rx.spacer(),
                    rx.button("Save Database", style=styles.BTN_TEAL, width="100%", on_click=State.save_database),
                    spacing="3",
                    align_items="start",
                    height="100%",
                ),
                padding="20px",
                background_color=styles.SURFACE_CONTAINER_LOWEST,
                border=f"1px solid {styles.BORDER}",
                border_radius="12px",
                width="100%",
            ),
            # Reload Card
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("refresh-cw", size=24, color=styles.PRIMARY_CONTAINER),
                        rx.text("Reload from Disk", font_size="16px", font_weight="700", color=styles.ON_SURFACE),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.text("Reloads clinic records from 'clinic_data.json' with corruption recovery.", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    rx.spacer(),
                    rx.button("Reload Data", style=styles.BTN_SECONDARY, width="100%", on_click=State.reload_database),
                    spacing="3",
                    align_items="start",
                    height="100%",
                ),
                padding="20px",
                background_color=styles.SURFACE_CONTAINER_LOWEST,
                border=f"1px solid {styles.BORDER}",
                border_radius="12px",
                width="100%",
            ),
            # Reset Card
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("octagon-alert", size=24, color=styles.ERROR),
                        rx.text("Reset Clinic Data", font_size="16px", font_weight="700", color=styles.ERROR),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.text("Permanently wipes all patient, doctor, and appointment records with confirmation.", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    rx.spacer(),
                    rx.button("Reset Database...", style=styles.BTN_DESTRUCTIVE, width="100%", on_click=State.prompt_reset_database),
                    spacing="3",
                    align_items="start",
                    height="100%",
                ),
                padding="20px",
                background_color=styles.SURFACE_CONTAINER_LOWEST,
                border=f"1px solid {styles.ERROR}",
                border_radius="12px",
                width="100%",
            ),
            columns={"initial": "1", "sm": "2", "md": "3"},
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


# =====================================================================
# MAIN STAFF PORTAL PAGE
# =====================================================================

def staff_page() -> rx.Component:
    """Main Staff Portal Layout."""
    return rx.box(
        # Fixed Sidebar on Desktop
        sidebar(),
        # Main Scrollable Workspace
        rx.box(
            navbar(breadcrumb="Staff Administration"),
            rx.box(
                # Top Workspace Welcome Header
                rx.hstack(
                    rx.vstack(
                        rx.text("Good morning, Staff", font_size=["22px", "26px"], font_weight="700", color=styles.ON_SURFACE, font_family=styles.FONT_HEADLINE),
                        rx.text("Saturday, September 13 • Clinic Operational Status: Normal Flow", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            "+ Quick Check-in",
                            variant="soft",
                            color_scheme="indigo",
                            size="2",
                            cursor="pointer",
                            on_click=State.open_patient_modal,
                        ),
                        rx.button(
                            "+ Book Appointment",
                            style=styles.BTN_PRIMARY,
                            size="2",
                            cursor="pointer",
                            on_click=State.open_booking_modal,
                        ),
                        spacing="2",
                    ),
                    align_items="center",
                    width="100%",
                    margin_bottom="20px",
                    flex_wrap="wrap",
                ),
                # Dynamic Content by Active Tab
                rx.match(
                    State.staff_active_tab,
                    ("dashboard", view_dashboard()),
                    ("queue", view_queue()),
                    ("patients", view_patients()),
                    ("doctors", view_doctors()),
                    ("reports", view_reports()),
                    ("admin", view_admin()),
                    view_dashboard(),
                ),
                padding=["16px", "24px", "32px"],
                max_width="1600px",
                margin="0 auto",
                width="100%",
            ),
            # Left padding matching 256px sidebar on large displays
            padding_left=["0", "0", "0", "256px"],
            width="100%",
            min_height="100vh",
            background_color=styles.SURFACE,
        ),
        # Modals
        booking_dialog(),
        patient_dialog(),
        doctor_dialog(),
        history_dialog(),
        confirmation_dialog(),
        width="100%",
        min_height="100vh",
        background_color=styles.SURFACE,
        on_mount=State.on_load,
    )
