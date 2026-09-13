import reflex as rx
from smart_clinic.web import styles
from smart_clinic.web.state import State


def clinic_emblem_logo(size: int = 36) -> rx.Component:
    """Render the official Smart Clinic emblem logo."""
    return rx.image(
        src="/clinic_logo.png",
        width=f"{size}px",
        height=f"{size}px",
        alt="Smart Clinic Emblem Logo",
        border_radius="6px",
    )


def navbar(breadcrumb: str = "Workspace") -> rx.Component:
    """Render top application navigation bar matching Stitch header."""
    return rx.box(
        rx.hstack(
            # Breadcrumbs
            rx.hstack(
                clinic_emblem_logo(28),
                rx.text(
                    "Smart Clinic",
                    font_size="14px",
                    font_weight="600",
                    color=styles.PRIMARY_CONTAINER,
                    font_family=styles.FONT_HEADLINE,
                ),
                rx.text("/", color=styles.OUTLINE_VARIANT, font_size="14px"),
                rx.text(
                    breadcrumb,
                    font_size="14px",
                    color=styles.ON_SURFACE,
                    font_weight="500",
                    font_family=styles.FONT_BODY,
                ),
                align_items="center",
                spacing="2",
            ),
            rx.spacer(),
            # Right Utilities
            rx.hstack(
                # Live Operational Clock Pill
                rx.box(
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            border_radius="9999px",
                            background_color=styles.SECONDARY_TEAL,
                        ),
                        rx.text(
                            "Live Operational Desk",
                            font_size="12px",
                            font_weight="500",
                            color=styles.ON_SURFACE,
                            font_family=styles.FONT_BODY,
                        ),
                        align_items="center",
                        spacing="2",
                    ),
                    padding_x="12px",
                    padding_y="6px",
                    border_radius="9999px",
                    background_color=styles.SURFACE_CONTAINER_LOW,
                    border=f"1px solid {styles.BORDER}",
                    display=["none", "none", "flex"],
                ),
                # Cloud Sync Pill
                rx.tooltip(
                    rx.button(
                        rx.hstack(
                            rx.box(
                                width="7px",
                                height="7px",
                                border_radius="9999px",
                                background_color=rx.cond(
                                    State.cloud_sync_status == "synced",
                                    styles.COMPLETED,
                                    styles.PENDING,
                                ),
                            ),
                            rx.text("Cloud Synced", font_size="11px", font_weight="600"),
                            spacing="1",
                            align_items="center",
                        ),
                        on_click=State.trigger_manual_cloud_sync,
                        loading=State.cloud_is_syncing,
                        size="1",
                        variant="soft",
                        color_scheme="teal",
                        cursor="pointer",
                        border_radius="9999px",
                    ),
                    content="Click to manually push & synchronize database with Cloud",
                ),
                # Triage Priority Pill
                rx.badge(
                    rx.hstack(
                        rx.box(
                            width="6px",
                            height="6px",
                            border_radius="9999px",
                            background_color=styles.ERROR,
                        ),
                        rx.text("TRIAGE LEVEL 1", font_size="11px", font_weight="700"),
                        align_items="center",
                        spacing="1",
                    ),
                    color_scheme="red",
                    variant="soft",
                    border_radius="9999px",
                    padding_x="10px",
                    padding_y="4px",
                ),
                # User Profile Chip
                rx.hstack(
                    rx.avatar(
                        src="/doctor_hero.png",
                        fallback=State.auth_role.upper()[:2],
                        size="1",
                        radius="full",
                        color_scheme="indigo",
                    ),
                    rx.vstack(
                        rx.text(
                            State.auth_display_name,
                            font_size="13px",
                            font_weight="600",
                            color=styles.ON_SURFACE,
                            line_height="1",
                        ),
                        rx.text(
                            State.auth_role.upper(),
                            font_size="11px",
                            color=styles.ON_SURFACE_VARIANT,
                            line_height="1",
                        ),
                        spacing="1",
                        align_items="start",
                        display=["none", "flex"],
                    ),
                    align_items="center",
                    spacing="2",
                    padding_x="8px",
                    padding_y="4px",
                    border_radius="8px",
                    background_color=styles.SURFACE_CONTAINER_LOW,
                ),
                # Logout Button
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("log-out", size=18, color=styles.ERROR),
                        on_click=State.logout,
                        variant="ghost",
                        size="2",
                        cursor="pointer",
                    ),
                    content="Logout / Exit",
                ),
                align_items="center",
                spacing="3",
            ),
            width="100%",
            height="64px",
            align_items="center",
            padding_x=["16px", "24px"],
        ),
        width="100%",
        height="64px",
        background_color=styles.SURFACE_CONTAINER_LOWEST,
        border_bottom=f"1px solid {styles.BORDER}",
        position="sticky",
        top="0",
        z_index="40",
        box_shadow="0 1px 4px rgba(0,0,0,0.02)",
    )
