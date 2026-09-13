import reflex as rx
from web import styles
from web.state import State


def booking_dialog() -> rx.Component:
    """Render Book Appointment Modal matching Stitch design reference."""
    return rx.dialog.root(
        rx.dialog.content(
            # Modal Header
            rx.box(
                rx.hstack(
                    rx.center(
                        rx.icon("calendar-plus", size=20, color=styles.PRIMARY_CONTAINER),
                        width="36px",
                        height="36px",
                        border_radius="8px",
                        background_color=styles.SURFACE_CONTAINER,
                    ),
                    rx.vstack(
                        rx.text(
                            "Book New Appointment",
                            font_size="18px",
                            font_weight="700",
                            color=styles.ON_SURFACE,
                            font_family=styles.FONT_HEADLINE,
                            line_height="1.2",
                        ),
                        rx.text(
                            "Schedule a 30-minute consultation slot with conflict detection",
                            font_size="13px",
                            color=styles.ON_SURFACE_VARIANT,
                            font_family=styles.FONT_BODY,
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
                            on_click=State.close_booking_modal,
                        )
                    ),
                    align_items="center",
                    width="100%",
                ),
                padding="18px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_bottom=f"1px solid {styles.BORDER}",
            ),
            # Modal Body Form
            rx.vstack(
                # Patient Selector
                rx.vstack(
                    rx.text(
                        "Patient Name / ID *",
                        font_size="13px",
                        font_weight="600",
                        color=styles.ON_SURFACE,
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Select registered patient..."),
                        rx.select.content(
                            rx.foreach(
                                State.patients_list,
                                lambda p: rx.select.item(p["name"], value=p["person_id"]),
                            )
                        ),
                        value=State.booking_patient_id,
                        on_change=State.set_booking_patient,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                # Doctor Selector
                rx.vstack(
                    rx.text(
                        "Attending Doctor *",
                        font_size="13px",
                        font_weight="600",
                        color=styles.ON_SURFACE,
                    ),
                    rx.select.root(
                        rx.select.trigger(placeholder="Select attending doctor..."),
                        rx.select.content(
                            rx.foreach(
                                State.doctors_list,
                                lambda d: rx.select.item(d["name"], value=d["person_id"]),
                            )
                        ),
                        value=State.booking_doctor_id,
                        on_change=State.set_booking_doctor,
                        width="100%",
                        size="3",
                    ),
                    width="100%",
                    spacing="1",
                    align_items="start",
                ),
                # Date and Time Grid
                rx.grid(
                    rx.vstack(
                        rx.text("Date *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            type="date",
                            value=State.booking_date_str,
                            on_change=State.set_booking_date,
                            width="100%",
                            size="3",
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.text("Time Slot (30m) *", font_size="13px", font_weight="600", color=styles.ON_SURFACE),
                        rx.input(
                            type="time",
                            value=State.booking_time_str,
                            on_change=State.set_booking_time,
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
                # Estimated Fee Notice
                rx.hstack(
                    rx.text("Slot Window:", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    rx.text("30 Minutes Busy Duration", font_size="13px", font_weight="600", color=styles.PRIMARY_CONTAINER),
                    rx.spacer(),
                    rx.text("Fee Rate:", font_size="13px", color=styles.ON_SURFACE_VARIANT),
                    rx.text("$100 Regular / $150 Emergency", font_size="13px", font_weight="700", color=styles.SECONDARY_TEAL),
                    width="100%",
                    padding="10px 14px",
                    background_color=styles.SURFACE_CONTAINER_LOW,
                    border_radius="8px",
                ),
                # STITCH PROMINENT CONFLICT ERROR BANNER
                rx.cond(
                    State.booking_has_conflict,
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("triangle-alert", size=20, color=styles.ERROR),
                                rx.text(
                                    "Time Slot Unavailable (30-Min Conflict Guard)",
                                    font_size="14px",
                                    font_weight="700",
                                    color=styles.ON_ERROR_CONTAINER,
                                ),
                                align_items="center",
                                spacing="2",
                            ),
                            rx.text(
                                State.booking_conflict_error,
                                font_size="13px",
                                color=styles.ON_ERROR_CONTAINER,
                                line_height="1.4",
                            ),
                            align_items="start",
                            spacing="1",
                        ),
                        padding="14px",
                        background_color=styles.ERROR_CONTAINER,
                        border=f"1px solid {styles.ERROR}",
                        border_radius="8px",
                        width="100%",
                    ),
                ),
                width="100%",
                padding="24px",
                spacing="4",
            ),
            # Modal Footer
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.icon("shield-check", size=16, color=styles.SECONDARY_TEAL),
                        rx.text("EMR 30-min conflict collision guard active", font_size="12px", color=styles.ON_SURFACE_VARIANT),
                        align_items="center",
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        size="3",
                        on_click=State.close_booking_modal,
                        cursor="pointer",
                    ),
                    rx.button(
                        "Book Appointment",
                        style=styles.BTN_PRIMARY,
                        size="3",
                        on_click=State.confirm_book_appointment,
                        disabled=State.booking_has_conflict,
                    ),
                    align_items="center",
                    width="100%",
                ),
                padding="16px 24px",
                background_color=styles.SURFACE_CONTAINER_LOW,
                border_top=f"1px solid {styles.BORDER}",
            ),
            max_width="560px",
            padding="0",
            border_radius="16px",
            overflow="hidden",
            background_color=styles.SURFACE_CONTAINER_LOWEST,
            box_shadow="0 20px 25px -5px rgba(15, 23, 42, 0.1)",
        ),
        open=State.booking_modal_open,
        on_open_change=State.close_booking_modal,
    )
