import reflex as rx
from smart_clinic.web import styles
from smart_clinic.web.state import State


def doctor_dialog() -> rx.Component:
    """Render Add Doctor Modal."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon("stethoscope", size=20, color=styles.SECONDARY_TEAL),
                        width="36px",
                        height="36px",
                        border_radius="8px",
                        background_color=styles.SURFACE_CONTAINER,
                    ),
                    rx.vstack(
                        rx.text(
                            "Add Medical Doctor",
                            font_size="18px",
                            font_weight="700",
                            color=styles.ON_SURFACE,
                            font_family=styles.FONT_HEADLINE,
                            line_height="1.2",
                        ),
                        rx.text(
                            "Register clinical specialist to clinic roster",
                            font_size="13px",
                            color=styles.ON_SURFACE_VARIANT,
                        ),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=18, color=styles.OUTLINE),
                            variant="ghost",
                            size="1",
                            cursor="pointer",
                            on_click=State.close_doctor_modal,
                        )
                    ),
                    align_items="center",
                    width="100%",
                ),
                padding="18px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_bottom=f"1px solid {styles.BORDER}",
            ),
            rx.vstack(
                rx.vstack(
                    rx.text("Doctor Name *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.input(
                        placeholder="e.g. Sara Mansoor",
                        value=State.new_doctor_name,
                        on_change=State.set_new_doctor_name,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Specialty *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.input(
                        placeholder="e.g. Cardiology, Internal Medicine, Pediatrics",
                        value=State.new_doctor_specialty,
                        on_change=State.set_new_doctor_specialty,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                rx.vstack(
                    rx.text("Contact Phone (01xxxxxxxxx) *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.input(
                        placeholder="e.g. 01198765432",
                        value=State.new_doctor_phone,
                        on_change=State.set_new_doctor_phone,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                rx.cond(
                    State.doctor_error_msg != "",
                    rx.callout(
                        State.doctor_error_msg,
                        icon="circle-alert",
                        color_scheme="red",
                        size="2",
                        width="100%",
                    ),
                ),
                width="100%",
                padding="24px",
                spacing="4",
            ),
            rx.box(
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        size="3",
                        on_click=State.close_doctor_modal,
                        cursor="pointer",
                    ),
                    rx.button(
                        "Add Doctor",
                        style=styles.BTN_TEAL,
                        size="3",
                        on_click=State.confirm_add_doctor,
                    ),
                    width="100%",
                    spacing="3",
                ),
                padding="16px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_top=f"1px solid {styles.BORDER}",
            ),
            max_width="500px",
            padding="0",
            border_radius="16px",
            overflow="hidden",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
        ),
        open=State.doctor_modal_open,
        on_open_change=State.close_doctor_modal,
    )
