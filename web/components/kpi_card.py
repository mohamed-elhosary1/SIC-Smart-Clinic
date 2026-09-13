import reflex as rx
from web import styles


def kpi_card(
    title: str,
    value: rx.Var | str,
    subtitle: rx.Var | str,
    icon_name: str,
    trend_text: str = "",
    trend_color: str = styles.SECONDARY_TEAL,
    icon_color: str = styles.PRIMARY_CONTAINER,
) -> rx.Component:
    """Render standardized healthcare KPI Card matching Stitch specifications."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    title,
                    font_size="13px",
                    font_weight="500",
                    color=styles.ON_SURFACE_VARIANT,
                    font_family=styles.FONT_BODY,
                ),
                rx.spacer(),
                rx.center(
                    rx.icon(icon_name, size=18, color=icon_color),
                    width="32px",
                    height="32px",
                    border_radius="8px",
                    background_color=styles.SURFACE_CONTAINER,
                ),
                width="100%",
                align_items="center",
            ),
            rx.text(
                value,
                font_size="32px",
                font_weight="700",
                color=styles.ON_SURFACE,
                font_family=styles.FONT_HEADLINE,
                letter_spacing="-0.02em",
                line_height="1.1",
                margin_top="6px",
            ),
            rx.divider(color=styles.BORDER, margin_y="6px"),
            rx.hstack(
                rx.text(
                    subtitle,
                    font_size="12px",
                    color=styles.ON_SURFACE_VARIANT,
                    font_family=styles.FONT_BODY,
                ),
                rx.spacer(),
                rx.cond(
                    trend_text != "",
                    rx.badge(
                        trend_text,
                        size="1",
                        color_scheme="teal" if trend_color == styles.SECONDARY_TEAL else "red",
                        variant="soft",
                        font_weight="600",
                        border_radius="4px",
                    ),
                ),
                width="100%",
                align_items="center",
            ),
            width="100%",
            spacing="1",
        ),
        padding="18px",
        background_color=styles.SURFACE_CONTAINER_LOWEST,
        border=f"1px solid {styles.BORDER}",
        border_radius="12px",
        box_shadow="0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px -1px rgba(15, 23, 42, 0.02)",
        transition="all 0.15s ease",
        _hover={"box_shadow": "0 4px 6px -1px rgba(15, 23, 42, 0.07)"},
        width="100%",
    )
