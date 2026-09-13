import reflex as rx
from web import styles


def empty_state(icon_name: str, title: str, description: str) -> rx.Component:
    """Render clean, centered healthcare empty state placeholder."""
    return rx.center(
        rx.vstack(
            rx.center(
                rx.icon(icon_name, size=32, color=styles.OUTLINE),
                width="64px",
                height="64px",
                border_radius="9999px",
                background_color=styles.SURFACE_CONTAINER_LOW,
            ),
            rx.text(
                title,
                font_size="16px",
                font_weight="600",
                color=styles.ON_SURFACE,
                font_family=styles.FONT_HEADLINE,
                margin_top="12px",
            ),
            rx.text(
                description,
                font_size="13px",
                color=styles.ON_SURFACE_VARIANT,
                font_family=styles.FONT_BODY,
                text_align="center",
                max_width="320px",
            ),
            align_items="center",
            spacing="1",
            padding="40px",
        ),
        width="100%",
        background_color=styles.SURFACE_CONTAINER_LOWEST,
        border=f"1px dashed {styles.BORDER}",
        border_radius="12px",
    )
