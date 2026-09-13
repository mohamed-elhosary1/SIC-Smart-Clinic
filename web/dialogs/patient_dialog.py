import reflex as rx
from web import styles
from web.state import State


def patient_dialog() -> rx.Component:
    """Render Register Patient Modal with Egyptian phone validation."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon("user-plus", size=20, color=styles.PRIMARY_CONTAINER),
                        width="36px",
                        height="36px",
                        border_radius="8px",
                        background_color=styles.SURFACE_CONTAINER,
                    ),
                    rx.vstack(
                        rx.text(
                            "Register New Patient",
                            font_size="18px",
                            font_weight="700",
                            color=styles.ON_SURFACE,
                            font_family=styles.FONT_HEADLINE,
                            line_height="1.2",
                        ),
                        rx.text(
                            "Create patient record with automatic ID generation",
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
                            on_click=State.close_patient_modal,
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
                    rx.text("Full Name *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.input(
                        placeholder="e.g. Mahmoud Ali",
                        value=State.new_patient_name,
                        on_change=State.set_new_patient_name,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Mobile Phone (01xxxxxxxxx) *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            placeholder="e.g. 01012345678",
                            value=State.new_patient_phone,
                            on_change=State.set_new_patient_phone,
                            width="100%",
                            size="3",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Age *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            placeholder="e.g. 28",
                            type="number",
                            value=State.new_patient_age,
                            on_change=State.set_new_patient_age,
                            width="100%",
                            size="3",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Case Type / Diagnosis Note", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                    rx.input(
                        placeholder="e.g. Migraine, Chest Pain, Hypertension...",
                        value=State.new_patient_case_type,
                        on_change=State.set_new_patient_case_type,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                # Triage Urgency Switch
                rx.hstack(
                    rx.vstack(
                        rx.text("High-Priority Emergency Case?", font_size="14px", font_weight="600", color=styles.ON_SURFACE),
                        rx.text("Emergency patients are assigned Priority Level 1 and preempt the queue", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                        spacing="0",
                        align_items="start",
                    ),
                    rx.spacer(),
                    rx.switch(
                        checked=State.new_patient_is_emergency,
                        on_change=State.set_new_patient_is_emergency,
                        color_scheme="red",
                    ),
                    width="100%",
                    padding="12px 14px",
                    background_color=styles.SURFACE_CONTAINER_LOW,
                    border_radius="8px",
                    align_items="center",
                ),
                rx.cond(
                    State.patient_error_msg != "",
                    rx.callout(
                        State.patient_error_msg,
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
                        on_click=State.close_patient_modal,
                        cursor="pointer",
                    ),
                    rx.button(
                        "Register Patient",
                        style=styles.BTN_PRIMARY,
                        size="3",
                        on_click=State.confirm_register_patient,
                    ),
                    width="100%",
                    spacing="3",
                ),
                padding="16px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_top=f"1px solid {styles.BORDER}",
            ),
            max_width="520px",
            padding="0",
            border_radius="16px",
            overflow="hidden",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
        ),
        open=State.patient_modal_open,
        on_open_change=State.close_patient_modal,
    )
