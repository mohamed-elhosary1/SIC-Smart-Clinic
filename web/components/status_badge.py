import reflex as rx
from web import styles


def priority_badge(priority_str: rx.Var[str] | str) -> rx.Component:
    """Render high-contrast Stitch-style priority badge with status dot."""
    return rx.cond(
        priority_str == "EMERGENCY",
        rx.badge(
            rx.box(
                width="6px",
                height="6px",
                border_radius="9999px",
                background_color=styles.ERROR,
            ),
            "EMERGENCY",
            size="2",
            color_scheme="red",
            variant="surface",
            font_family=styles.FONT_BODY,
            font_weight="700",
            letter_spacing="0.04em",
            padding_x="8px",
            padding_y="4px",
            border_radius="9999px",
        ),
        rx.badge(
            rx.box(
                width="6px",
                height="6px",
                border_radius="9999px",
                background_color=styles.REGULAR,
            ),
            "REGULAR",
            size="2",
            color_scheme="blue",
            variant="surface",
            font_family=styles.FONT_BODY,
            font_weight="600",
            letter_spacing="0.04em",
            padding_x="8px",
            padding_y="4px",
            border_radius="9999px",
        ),
    )


def status_badge(status_str: rx.Var[str] | str) -> rx.Component:
    """Render clinical status pill (WAITING, IN CONSULTATION, COMPLETED, CANCELLED)."""
    return rx.match(
        status_str,
        ("PENDING", rx.badge("WAITING", size="2", color_scheme="amber", variant="surface", font_weight="600", border_radius="9999px", padding_x="8px")),
        ("IN PROGRESS", rx.badge("IN CONSULTATION", size="2", color_scheme="blue", variant="surface", font_weight="600", border_radius="9999px", padding_x="8px")),
        ("COMPLETED", rx.badge("COMPLETED", size="2", color_scheme="green", variant="surface", font_weight="600", border_radius="9999px", padding_x="8px")),
        ("CANCELLED", rx.badge("CANCELLED", size="2", color_scheme="gray", variant="surface", font_weight="600", border_radius="9999px", padding_x="8px")),
        rx.badge(status_str, size="2", color_scheme="gray", variant="surface", border_radius="9999px", padding_x="8px"),
    )
