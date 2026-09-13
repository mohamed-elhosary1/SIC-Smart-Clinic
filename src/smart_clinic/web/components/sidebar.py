import reflex as rx
from smart_clinic.web import styles
from smart_clinic.web.state import State
from smart_clinic.web.components.navbar import clinic_emblem_logo


def sidebar_nav_item(label: str, icon_name: str, tab_id: str) -> rx.Component:
    """Render sidebar navigation link with active highlight."""
    is_active = State.staff_active_tab == tab_id
    return rx.box(
        rx.hstack(
            rx.icon(
                icon_name,
                size=20,
                color=rx.cond(is_active, styles.ON_PRIMARY, styles.ON_SURFACE_VARIANT),
            ),
            rx.text(
                label,
                font_size="14px",
                font_weight=rx.cond(is_active, "600", "500"),
                color=rx.cond(is_active, styles.ON_PRIMARY, styles.ON_SURFACE_VARIANT),
                font_family=styles.FONT_BODY,
            ),
            align_items="center",
            spacing="3",
            width="100%",
        ),
        padding_x="14px",
        padding_y="10px",
        border_radius="8px",
        background_color=rx.cond(is_active, styles.PRIMARY_CONTAINER, "transparent"),
        box_shadow=rx.cond(is_active, "0 1px 2px rgba(0,0,0,0.05)", "none"),
        cursor="pointer",
        transition="all 0.15s ease",
        _hover={
            "background_color": rx.cond(is_active, styles.PRIMARY_CONTAINER, styles.SURFACE_CONTAINER),
        },
        on_click=State.set_staff_tab(tab_id),
        width="100%",
    )


def sidebar() -> rx.Component:
    """Render persistent 256px sidebar matching Stitch specification."""
    return rx.box(
        rx.vstack(
            # Sidebar Header
            rx.hstack(
                clinic_emblem_logo(32),
                rx.vstack(
                    rx.text(
                        "SMART CLINIC",
                        font_size="15px",
                        font_weight="700",
                        color=styles.PRIMARY_CONTAINER,
                        font_family=styles.FONT_HEADLINE,
                        letter_spacing="-0.01em",
                        line_height="1.1",
                    ),
                    rx.text(
                        "Intelligent Management",
                        font_size="11px",
                        color=styles.ON_SURFACE_VARIANT,
                        font_family=styles.FONT_BODY,
                        line_height="1",
                    ),
                    spacing="0",
                    align_items="start",
                ),
                align_items="center",
                spacing="3",
                padding_x="16px",
                padding_y="18px",
                border_bottom=f"1px solid {styles.BORDER}",
                width="100%",
            ),
            # Section Tag
            rx.text(
                "CLINICAL NAVIGATION",
                font_size="11px",
                font_weight="600",
                color=styles.OUTLINE,
                letter_spacing="0.06em",
                padding_x="16px",
                padding_top="16px",
                padding_bottom="6px",
                width="100%",
            ),
            # Main Navigation Links
            rx.vstack(
                sidebar_nav_item("Dashboard", "layout-dashboard", "dashboard"),
                sidebar_nav_item("Queue & Appointments", "calendar-check", "queue"),
                sidebar_nav_item("Patients", "users", "patients"),
                sidebar_nav_item("Doctors", "stethoscope", "doctors"),
                sidebar_nav_item("Reports", "bar-chart-3", "reports"),
                sidebar_nav_item("Administration", "shield-check", "admin"),
                spacing="1",
                padding_x="10px",
                width="100%",
            ),
            rx.spacer(),
            # Bottom Actions
            rx.divider(color=styles.BORDER),
            rx.vstack(
                rx.box(
                    rx.hstack(
                        rx.icon("save", size=18, color=styles.SECONDARY_TEAL),
                        rx.text("Save Database", font_size="13px", font_weight="500", color=styles.ON_SURFACE),
                        align_items="center",
                        spacing="3",
                    ),
                    padding_x="14px",
                    padding_y="9px",
                    border_radius="8px",
                    cursor="pointer",
                    _hover={"background_color": styles.SURFACE_CONTAINER},
                    on_click=State.save_database,
                    width="100%",
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("log-out", size=18, color=styles.ERROR),
                        rx.text("Logout", font_size="13px", font_weight="500", color=styles.ERROR),
                        align_items="center",
                        spacing="3",
                    ),
                    padding_x="14px",
                    padding_y="9px",
                    border_radius="8px",
                    cursor="pointer",
                    _hover={"background_color": styles.ERROR_CONTAINER},
                    on_click=State.logout,
                    width="100%",
                ),
                spacing="1",
                padding_x="10px",
                padding_bottom="16px",
                width="100%",
            ),
            height="100%",
            width="100%",
            spacing="0",
        ),
        width="256px",
        height="100vh",
        position="fixed",
        left="0",
        top="0",
        background_color=styles.SURFACE_CONTAINER_LOWEST,
        border_right=f"1px solid {styles.BORDER}",
        z_index="50",
        display=["none", "none", "none", "block"],
    )
