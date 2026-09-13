import reflex as rx
from smart_clinic.web import styles
from smart_clinic.web.state import State


def confirmation_dialog() -> rx.Component:
    """Render destructive action confirmation dialog."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(State.confirm_title),
            rx.alert_dialog.description(
                State.confirm_message,
                size="2",
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=State.close_confirm_modal,
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Confirm Action",
                        color_scheme="red",
                        variant="solid",
                        on_click=State.execute_confirm_action,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="450px",
        ),
        open=State.confirm_modal_open,
        on_open_change=State.close_confirm_modal,
    )
